import sqlite3 from 'sqlite3';
import path from 'path';

export async function GET() {
  return new Promise((resolve) => {
    try {
      // The weather.db is one level up from the weather-dashboard directory
      // Depending on how Next.js runs, process.cwd() is the root of the weather-dashboard project
      const dbPath = path.resolve(process.cwd(), '../weather.db');
      
      const db = new sqlite3.Database(dbPath, sqlite3.OPEN_READONLY, (err) => {
        if (err) {
          resolve(Response.json({ success: false, error: 'Database connection failed: ' + err.message }, { status: 500 }));
        }
      });

      // Fetch the latest 100 records
      db.all('SELECT * FROM weather ORDER BY time DESC LIMIT 100', [], (err, rows) => {
        db.close();
        if (err) {
          resolve(Response.json({ success: false, error: err.message }, { status: 500 }));
        } else {
          resolve(Response.json({ success: true, data: rows }));
        }
      });
    } catch (error) {
      resolve(Response.json({ success: false, error: error.message }, { status: 500 }));
    }
  });
}
