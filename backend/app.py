from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import mysql.connector
import hashlib
import uuid
from datetime import datetime, timedelta
import jwt
import platform
import hashlib
import csv
import io

app = Flask(__name__)
# 允许前端访问
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3002"]  # 只允许 3002 端口访问
    }
})

# 数据库配置
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',  # 修改为你的MySQL密码
    'database': 'license_system',
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci'
}

# JWT密钥
SECRET_KEY = "your_secret_key"

def get_db_connection():
    return mysql.connector.connect(**db_config)

def get_machine_code():
    """获取机器码"""
    system_info = platform.uname()
    machine_info = f"{system_info.system}{system_info.machine}{system_info.processor}"
    return hashlib.md5(machine_info.encode()).hexdigest()

# 验证token的装饰器
def require_token(f):
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'No token provided'}), 401
        try:
            token = auth_header.split(' ')[1]
            jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except Exception as e:
            return jsonify({'error': f'Invalid token: {str(e)}'}), 401
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT * FROM users 
        WHERE username = %s AND password = SHA2(%s, 256)
    """, (username, password))
    
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if user:
        token = jwt.encode(
            {'user_id': user['id'], 'exp': datetime.utcnow().timestamp() + 24*3600},
            SECRET_KEY,
            algorithm='HS256'
        )
        return jsonify({'token': token})
    
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/verify_license', methods=['POST'])
def verify_license():
    data = request.get_json()
    license_key = data.get('license_key')
    machine_code = data.get('machine_code', get_machine_code())
    
    if not license_key:
        return jsonify({'error': 'License key is required'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # 检查许可证是否有效
    cursor.execute("""
        SELECT l.*, COUNT(mb.id) as bound_machines 
        FROM licenses l 
        LEFT JOIN machine_bindings mb ON l.id = mb.license_id
        WHERE l.license_key = %s AND l.is_active = TRUE 
        AND (l.expire_date IS NULL OR l.expire_date > NOW())
        GROUP BY l.id
    """, (license_key,))
    
    license = cursor.fetchone()
    
    if not license:
        cursor.close()
        conn.close()
        return jsonify({'valid': False, 'error': 'Invalid or expired license'})
    
    # 检查机器绑定
    cursor.execute("""
        SELECT * FROM machine_bindings 
        WHERE license_id = %s AND machine_code = %s
    """, (license['id'], machine_code))
    
    binding = cursor.fetchone()
    
    if not binding and license['bound_machines'] >= license['max_machines']:
        cursor.close()
        conn.close()
        return jsonify({'valid': False, 'error': 'Maximum number of machines reached'})
    
    # 记录使用情况
    cursor.execute("""
        INSERT INTO usage_logs (license_id, machine_code, action)
        VALUES (%s, %s, 'verify')
    """, (license['id'], machine_code))
    
    # 更新最后使用时间
    cursor.execute("""
        UPDATE licenses SET last_used = NOW()
        WHERE id = %s
    """, (license['id'],))
    
    # 如果是新机器，添加绑定
    if not binding:
        cursor.execute("""
            INSERT INTO machine_bindings (license_id, machine_code)
            VALUES (%s, %s)
        """, (license['id'], machine_code))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({'valid': True})

@app.route('/api/generate_license', methods=['POST'])
@require_token
def generate_license():
    data = request.get_json()
    max_machines = data.get('max_machines', 1)
    expire_days = data.get('expire_days', 365)
    batch_size = data.get('batch_size', 1)
    notes = data.get('notes', '')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    batch_id = str(uuid.uuid4()) if batch_size > 1 else None
    licenses = []
    
    try:
        for _ in range(batch_size):
            license_key = str(uuid.uuid4())
            expire_date = datetime.now() + timedelta(days=expire_days)
            
            cursor.execute("""
                INSERT INTO licenses (license_key, expire_date, max_machines, batch_id, notes)
                VALUES (%s, %s, %s, %s, %s)
            """, (license_key, expire_date, max_machines, batch_id, notes))
            
            licenses.append(license_key)
        
        conn.commit()
        print(f"Generated {len(licenses)} license(s)")
    except Exception as e:
        print(f"Database error: {str(e)}")
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    finally:
        cursor.close()
        conn.close()
    
    return jsonify({'licenses': licenses})

@app.route('/api/licenses', methods=['GET'])
@require_token
def get_licenses():
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('pageSize', 10))
    offset = (page - 1) * page_size
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # 获取总记录数
    cursor.execute("""
        SELECT COUNT(*) as total FROM licenses
    """)
    total = cursor.fetchone()['total']
    
    # 获取分页数据
    cursor.execute("""
        SELECT l.*, 
               COUNT(DISTINCT mb.machine_code) as active_machines,
               COUNT(DISTINCT ul.id) as usage_count
        FROM licenses l
        LEFT JOIN machine_bindings mb ON l.id = mb.license_id
        LEFT JOIN usage_logs ul ON l.id = ul.license_id
        GROUP BY l.id
        ORDER BY l.created_at DESC
        LIMIT %s OFFSET %s
    """, (page_size, offset))
    
    licenses = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return jsonify({
        'items': licenses,
        'total': total,
        'page': page,
        'pageSize': page_size
    })

@app.route('/api/deactivate_license/<license_key>', methods=['POST'])
@require_token
def deactivate_license(license_key):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE licenses SET is_active = FALSE
            WHERE license_key = %s
        """, (license_key,))
        
        conn.commit()
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()
    
    return jsonify({'message': 'License deactivated successfully'})

@app.route('/api/renew_license/<license_key>', methods=['POST'])
@require_token
def renew_license(license_key):
    data = request.get_json()
    days = data.get('days', 365)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 同时更新过期时间和激活状态
        cursor.execute("""
            UPDATE licenses 
            SET expire_date = DATE_ADD(COALESCE(expire_date, NOW()), INTERVAL %s DAY),
                is_active = TRUE
            WHERE license_key = %s
        """, (days, license_key))
        
        conn.commit()
        
        # 验证更新是否成功
        cursor.execute("""
            SELECT * FROM licenses WHERE license_key = %s
        """, (license_key,))
        
        if cursor.fetchone():
            return jsonify({'message': 'License renewed successfully'})
        else:
            return jsonify({'error': 'License not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/license/<license_key>', methods=['GET'])
@require_token
def get_license_details(license_key):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT l.*, 
               COUNT(DISTINCT mb.machine_code) as active_machines,
               COUNT(DISTINCT ul.id) as usage_count,
               GROUP_CONCAT(DISTINCT mb.machine_code) as bound_machines
        FROM licenses l
        LEFT JOIN machine_bindings mb ON l.id = mb.license_id
        LEFT JOIN usage_logs ul ON l.id = ul.license_id
        WHERE l.license_key = %s
        GROUP BY l.id
    """, (license_key,))
    
    license = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not license:
        return jsonify({'error': 'License not found'}), 404
        
    return jsonify(license)

@app.route('/api/batch/deactivate', methods=['POST'])
@require_token
def batch_deactivate():
    data = request.get_json()
    license_keys = data.get('licenseKeys', [])
    
    if not license_keys:
        return jsonify({'error': 'No license keys provided'}), 400
        
    print(f"Deactivating licenses: {license_keys}")  # 添加调试日志
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 对每个许可证单独执行更新
        for license_key in license_keys:
            cursor.execute("""
                UPDATE licenses 
                SET is_active = FALSE
                WHERE license_key = %s
            """, (license_key,))
        
        conn.commit()
        return jsonify({'message': f'{len(license_keys)} licenses deactivated'})
    except Exception as e:
        print(f"Error deactivating licenses: {str(e)}")  # 添加错误日志
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/batch/renew', methods=['POST'])
@require_token
def batch_renew():
    data = request.get_json()
    license_keys = data.get('licenseKeys', [])
    days = data.get('days', 365)
    
    if not license_keys:
        return jsonify({'error': 'No license keys provided'}), 400
        
    print(f"Renewing licenses: {license_keys} for {days} days")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 对每个许可证单独执行更新
        for license_key in license_keys:
            cursor.execute("""
                UPDATE licenses 
                SET expire_date = DATE_ADD(COALESCE(expire_date, NOW()), INTERVAL %s DAY),
                    is_active = TRUE
                WHERE license_key = %s
            """, (days, license_key))
        
        conn.commit()
        
        # 验证更新结果
        placeholders = ','.join(['%s'] * len(license_keys))
        cursor.execute(f"""
            SELECT COUNT(*) as updated_count
            FROM licenses 
            WHERE license_key IN ({placeholders})
            AND is_active = TRUE
            AND expire_date > NOW()
        """, tuple(license_keys))
        
        result = cursor.fetchone()
        updated_count = result[0] if result else 0
        
        return jsonify({
            'message': f'{updated_count} licenses renewed successfully',
            'updated_count': updated_count
        })
        
    except Exception as e:
        print(f"Error renewing licenses: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/licenses/export', methods=['GET'])
@require_token
def export_licenses():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT 
            l.license_key,
            l.is_active,
            l.expire_date,
            l.created_at,
            l.max_machines,
            COUNT(DISTINCT mb.machine_code) as active_machines,
            l.notes
        FROM licenses l
        LEFT JOIN machine_bindings mb ON l.id = mb.license_id
        GROUP BY l.id
        ORDER BY l.created_at DESC
    """)
    
    licenses = cursor.fetchall()
    cursor.close()
    conn.close()
    
    # 创建CSV格式的数据
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=licenses[0].keys())
    writer.writeheader()
    writer.writerows(licenses)
    
    # 创建响应
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=licenses.csv'
    
    return response

@app.route('/api/licenses/search', methods=['GET'])
@require_token
def search_licenses():
    query = request.args.get('query', '')
    status = request.args.get('status')
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('pageSize', 10))
    offset = (page - 1) * page_size
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # 构建查询条件
    where_clause = "WHERE 1=1"
    params = []
    
    if query:
        where_clause += " AND l.license_key LIKE %s"
        params.append(f'%{query}%')
    
    if status:
        where_clause += " AND l.is_active = %s"
        params.append(status == 'active')
    
    # 获取总记录数
    count_sql = f"""
        SELECT COUNT(*) as total 
        FROM licenses l 
        {where_clause}
    """
    cursor.execute(count_sql, params)
    total = cursor.fetchone()['total']
    
    # 获取分页数据
    sql = f"""
        SELECT l.*, 
               COUNT(DISTINCT mb.machine_code) as active_machines
        FROM licenses l
        LEFT JOIN machine_bindings mb ON l.id = mb.license_id
        {where_clause}
        GROUP BY l.id
        ORDER BY l.created_at DESC
        LIMIT %s OFFSET %s
    """
    cursor.execute(sql, params + [page_size, offset])
    
    licenses = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return jsonify({
        'items': licenses,
        'total': total,
        'page': page,
        'pageSize': page_size
    })

@app.route('/api/license/<license_key>/note', methods=['POST'])
@require_token
def update_license_note(license_key):
    data = request.get_json()
    note = data.get('note', '')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE licenses 
            SET notes = %s
            WHERE license_key = %s
        """, (note, license_key))
        
        conn.commit()
        return jsonify({'message': 'Note updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/')
def index():
    return jsonify({
        'message': 'Welcome to License System API',
        'endpoints': {
            'login': '/api/login',
            'verify_license': '/api/verify_license',
            'generate_license': '/api/generate_license',
            'get_licenses': '/api/licenses',
            'deactivate_license': '/api/deactivate_license/<license_key>',
            'renew_license': '/api/renew_license/<license_key>',
            'get_license_details': '/api/license/<license_key>',
            'batch_deactivate': '/api/batch/deactivate',
            'batch_renew': '/api/batch/renew',
            'export_licenses': '/api/licenses/export',
            'search_licenses': '/api/licenses/search'
        }
    })

if __name__ == '__main__':
    app.run(debug=True) 