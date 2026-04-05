'use client';

import { useEffect, useState } from 'react';
import styles from './page.module.css';
import { Thermometer, Wind, RefreshCw, Compass } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { formatInTimeZone } from 'date-fns-tz';

export default function Dashboard() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(new Date());

  const fetchData = async () => {
    try {
      const res = await fetch('/api/weather');
      const result = await res.json();
      if (result.success) {
        setData(result.data.reverse());
        setLastUpdated(new Date());
        setError(null);
      } else {
        setError(result.error);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const intervalId = setInterval(fetchData, 60 * 1000);
    return () => clearInterval(intervalId);
  }, []);

  if (loading && data.length === 0) return (
    <div className={styles.loading}>
      <RefreshCw className={styles.pulse} size={32} />
      Connecting to Database...
    </div>
  );
  
  if (error) return <div className={styles.error}>Error: {error}</div>;

  const chartData = data.map(d => {
    let tempValue = 0;
    if (d.temperature) {
      const match = d.temperature.match(/[\d.]+/);
      if (match) tempValue = parseFloat(match[0]);
    }
    
    let utcTimeStr = null;
    let timeFormatted = '';
    if (d.time) {
      // Append Z to parse SQLite datetime correctly as UTC
      utcTimeStr = d.time.replace(' ', 'T') + 'Z';
      timeFormatted = formatInTimeZone(new Date(utcTimeStr), 'Asia/Manila', 'HH:mm');
    }
    
    return {
      ...d,
      tempValue,
      timeFormatted,
      utcTimeStr
    };
  });

  const latest = chartData[chartData.length - 1] || {};

  return (
    <main className={styles.container}>
      <header className={styles.header}>
        <h1 className={styles.title}>Weather Systems Dashboard</h1>
        <div className={styles.statusIndicator}>
          <div className={styles.pulse}></div>
          Live • Last updated {formatInTimeZone(lastUpdated, 'Asia/Manila', 'HH:mm:ss')}
        </div>
      </header>

      <section className={styles.cardsGrid}>
        <div className={styles.card}>
          <div className={styles.cardHeader}>
            <Thermometer className={styles.icon} size={24} />
            Current Temperature
          </div>
          <div className={styles.cardValue}>{latest.temperature || '--'}</div>
          <div className={styles.cardSub}>Recorded at {latest.utcTimeStr ? formatInTimeZone(new Date(latest.utcTimeStr), 'Asia/Manila', 'PPp') : '--'}</div>
        </div>

        <div className={styles.card}>
          <div className={styles.cardHeader}>
            <Wind className={styles.icon} size={24} />
            Wind Speed
          </div>
          <div className={styles.cardValue}>{latest.windspeed || '--'}</div>
          <div className={styles.cardSub}>Surface winds</div>
        </div>

        <div className={styles.card}>
          <div className={styles.cardHeader}>
            <Compass className={styles.icon} size={24} />
            Wind Direction
          </div>
          <div className={styles.cardValue}>{latest.wind_direction || '--'}°</div>
          <div className={styles.cardSub}>Direction angle</div>
        </div>
      </section>

      <section className={styles.chartContainer}>
        <h2 className={styles.chartTitle}>Temperature Trends</h2>
        <div style={{ width: '100%', height: 'calc(100% - 3rem)' }}>
          <ResponsiveContainer>
            <LineChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#eaeaea" />
              <XAxis dataKey="timeFormatted" stroke="#666666" />
              <YAxis stroke="#666666" domain={['dataMin - 1', 'dataMax + 1']} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#ffffff', border: '1px solid #eaeaea', borderRadius: '8px', color: '#111111' }}
                labelStyle={{ color: '#0070f3', fontWeight: 'bold' }}
              />
              <Line type="monotone" dataKey="tempValue" name="Temp (°C)" stroke="#0070f3" strokeWidth={3} dot={{ fill: '#0070f3', r: 4, strokeWidth: 0 }} activeDot={{ r: 6, stroke: '#ffffff', strokeWidth: 2 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </section>

      <section className={styles.tableContainer}>
        <h2 className={styles.tableTitle}>Historical Log</h2>
        <div style={{ overflowX: 'auto' }}>
          <table className={styles.historyTable}>
            <thead>
              <tr>
                <th>Time (PH)</th>
                <th>Temperature</th>
                <th>Wind Speed</th>
                <th>Wind Direction</th>
              </tr>
            </thead>
            <tbody>
              {[...chartData].reverse().map((row, index) => (
                <tr key={index}>
                  <td>{row.utcTimeStr ? formatInTimeZone(new Date(row.utcTimeStr), 'Asia/Manila', 'MMM d, p') : '--'}</td>
                  <td>{row.temperature || '--'}</td>
                  <td>{row.windspeed || '--'}</td>
                  <td>{row.wind_direction ? `${row.wind_direction}°` : '--'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </main>
  );
}
