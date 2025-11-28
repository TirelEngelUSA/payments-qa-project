CREATE TABLE IF NOT EXISTS payments (
  id SERIAL PRIMARY KEY,
  user_id INT,
  amount INT,
  status VARCHAR(20) DEFAULT 'PROCESSING',
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS taxes (
  id SERIAL PRIMARY KEY,
  payment_id INT,
  tax_amount INT,
  created_at TIMESTAMP DEFAULT now()
);