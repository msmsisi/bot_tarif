import sqlite3

class Database:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS currency (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                currency TEXT UNIQUE,
                rate REAL
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS delivery (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                country TEXT,
                city TEXT,
                tariff_type TEXT,
                delivery_time TEXT,
                cost_per_kg REAL,
                fixed_cost REAL,
                UNIQUE(country, city, tariff_type)
            )
        """)
        self.conn.commit()

    def update_currency_rate(self, currency, rate):
        self.cursor.execute("INSERT OR REPLACE INTO currency (currency, rate) VALUES (?, ?)", (currency, rate))
        self.conn.commit()

    def get_currency_rate(self, currency):
        self.cursor.execute("SELECT rate FROM currency WHERE currency = ?", (currency,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def get_all_currencies(self):
        self.cursor.execute("SELECT currency FROM currency")
        result = self.cursor.fetchall()
        return [item[0] for item in result]

    def add_delivery_tariff(self, country, city, tariff_type, delivery_time, cost_per_kg, fixed_cost):
        self.cursor.execute("""
            INSERT INTO delivery (country, city, tariff_type, delivery_time, cost_per_kg, fixed_cost)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(country, city, tariff_type) DO UPDATE SET
                delivery_time = excluded.delivery_time,
                cost_per_kg = excluded.cost_per_kg,
                fixed_cost = excluded.fixed_cost
        """, (country, city, tariff_type, delivery_time, cost_per_kg, fixed_cost))
        self.conn.commit()

    def get_delivery_tariff(self, country):
      self.cursor.execute("SELECT tariff_type, delivery_time, cost_per_kg, fixed_cost FROM delivery WHERE country=?", (country,))
      result = self.cursor.fetchall()
      return result if result else None

    def close(self):
        self.conn.close()

    def delete_delivery_tariff(self, country, city):
      self.cursor.execute("DELETE FROM delivery WHERE country=? AND city=?", (country, city,))
      self.conn.commit()
    
    def get_all_delivery_countries(self):
      """
      Получает все уникальные страны из таблицы delivery.
      """
      self.cursor.execute("SELECT DISTINCT country FROM delivery")
      countries = self.cursor.fetchall()
      return [country[0] for country in countries]

    def get_all_delivery_cities_by_country(self, country):
      """
      Получает все уникальные города для указанной страны из таблицы delivery.
      """
      self.cursor.execute("SELECT DISTINCT city FROM delivery WHERE country=?", (country,))
      cities = self.cursor.fetchall()
      return [city[0] for city in cities]
    
    def get_tariffs_by_city(self, city):
        """
        Получает все тарифы для указанного города.
        """
        self.cursor.execute("SELECT tariff_type, delivery_time, cost_per_kg, fixed_cost FROM delivery WHERE city=?", (city,))
        tariffs = self.cursor.fetchall()
        return tariffs
