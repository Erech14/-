from flask import Flask, render_template, request, jsonify
import pandas as pd
import os

app = Flask(__name__)

# Загрузка данных из CSV
csv_path = os.path.join(os.path.dirname(__file__), 'foods.csv')
df = pd.read_csv(csv_path)

# Очистка данных
df.columns = ['product', 'carbs']
df['carbs_value'] = df['carbs'].str.replace(' г', '').astype(float)
df = df.sort_values('carbs_value', ascending=False)


@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')


@app.route('/api/search', methods=['GET'])
def search():
    """API для поиска продуктов"""
    query = request.args.get('q', '').lower()
    
    if not query:
        # Если нет поиска, возвращаем топ 20 продуктов по углеводам
        results = df.head(20).to_dict('records')
    else:
        # Фильтруем по названию продукта
        filtered = df[df['product'].str.lower().str.contains(query, na=False)]
        results = filtered.head(30).to_dict('records')
    
    return jsonify({
        'success': True,
        'count': len(results),
        'data': results
    })


@app.route('/api/all', methods=['GET'])
def get_all():
    """Получить все продукты с пагинацией"""
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    start = (page - 1) * per_page
    end = start + per_page
    
    total = len(df)
    results = df.iloc[start:end].to_dict('records')
    
    return jsonify({
        'success': True,
        'page': page,
        'per_page': per_page,
        'total': total,
        'total_pages': (total + per_page - 1) // per_page,
        'data': results
    })


@app.route('/api/sort', methods=['GET'])
def sort_products():
    """Сортировка продуктов"""
    sort_by = request.args.get('sort_by', 'carbs_value')
    order = request.args.get('order', 'desc')
    
    ascending = order.lower() == 'asc'
    sorted_df = df.sort_values(sort_by, ascending=ascending)
    
    results = sorted_df.head(50).to_dict('records')
    
    return jsonify({
        'success': True,
        'count': len(results),
        'data': results
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)
