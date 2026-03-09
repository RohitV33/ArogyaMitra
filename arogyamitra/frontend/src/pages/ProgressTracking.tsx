// ProgressTracking.tsx - Activity 4.2 (Progress module)
// Matches the BodyMetrics interface and state structure from screenshots

import React, { useState, useEffect } from 'react';

// ─── BodyMetrics Interface (exact from screenshot) ────────────────────────────
interface BodyMetrics {
  bmi?: number;
  bodyFatPercent?: number;
  muscleMass?: number;
  waistCircumference?: number;
  age?: number;
  gender?: string;
  height?: number;
  weight?: number;
  timestamp?: string;
}

// ─── Component (state matching screenshot exactly) ────────────────────────────
const ProgressTracking: React.FC = () => {
  const [selectedPeriod, setSelectedPeriod] = useState<'week' | 'month' | '3months' | 'year'>('month');
  const [activeTab, setActiveTab] = useState<'overview' | 'workouts' | 'nutrition' | 'body' | 'achievements'>('overview');
  const [workoutCount, setWorkoutCount] = useState(0);
  const [caloriesBurned, setCaloriesBurned] = useState(0);
  const [mealTracked, setMealTracked] = useState(0);
  const [bodyMetrics, setBodyMetrics] = useState<BodyMetrics | null>(null);

  useEffect(() => {
    // Load body metrics from localStorage (as shown in screenshot)
    const bodyMetricsStr = localStorage.getItem('body-metrics');
    const metrics = bodyMetricsStr ? JSON.parse(bodyMetricsStr) : {};
    setBodyMetrics(metrics);

    // Load progress stats
    fetch('https://arogyamitra-o8sd.onrender.com/api/progress/analytics', {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('arogyamitra_token')}`,
      },
    })
      .then((r) => r.json())
      .then((data) => {
        setWorkoutCount(data.workouts_completed || 0);
        setCaloriesBurned(
          data.weight_history?.reduce((acc: number, w: number) => acc, 0) || 0
        );
      })
      .catch(() => {});
  }, [selectedPeriod]);

  return (
    <div style={{ padding: '32px', maxWidth: '1100px' }}>
      <h1
        style={{
          fontFamily: 'Syne, sans-serif',
          fontSize: '1.8rem',
          fontWeight: 800,
          marginBottom: '4px',
        }}
      >
        Progress Tracking
      </h1>
      <p style={{ color: '#7a9bb5', marginBottom: '24px' }}>
        Monitor your fitness journey with detailed analytics
      </p>

      {/* Period Selector */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '24px' }}>
        {(['week', 'month', '3months', 'year'] as const).map((period) => (
          <button
            key={period}
            onClick={() => setSelectedPeriod(period)}
            style={{
              padding: '8px 16px',
              borderRadius: '8px',
              border: `1px solid ${selectedPeriod === period ? '#00d4aa' : 'rgba(0,212,170,0.15)'}`,
              background: selectedPeriod === period ? 'rgba(0,212,170,0.15)' : 'transparent',
              color: selectedPeriod === period ? '#00d4aa' : '#7a9bb5',
              cursor: 'pointer',
              fontFamily: 'inherit',
              fontWeight: 500,
              fontSize: '0.85rem',
              transition: 'all 0.2s',
            }}
          >
            {period === '3months' ? '3 Months' : period.charAt(0).toUpperCase() + period.slice(1)}
          </button>
        ))}
      </div>

      {/* Tab Selector */}
      <div
        style={{
          display: 'flex',
          gap: '4px',
          marginBottom: '24px',
          background: 'rgba(255,255,255,0.03)',
          padding: '4px',
          borderRadius: '10px',
          border: '1px solid rgba(0,212,170,0.1)',
          width: 'fit-content',
        }}
      >
        {(['overview', 'workouts', 'nutrition', 'body', 'achievements'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{
              padding: '8px 16px',
              borderRadius: '7px',
              border: 'none',
              background: activeTab === tab ? 'linear-gradient(135deg, #00d4aa20, #0099ff20)' : 'transparent',
              color: activeTab === tab ? '#00d4aa' : '#7a9bb5',
              cursor: 'pointer',
              fontFamily: 'inherit',
              fontWeight: activeTab === tab ? 600 : 400,
              fontSize: '0.85rem',
              transition: 'all 0.2s',
              textTransform: 'capitalize',
            }}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
          {[
            { icon: '🏋️', label: 'Workouts', value: workoutCount, sub: `this ${selectedPeriod}`, color: '#00d4aa' },
            { icon: '🔥', label: 'Calories Burned', value: `${caloriesBurned}`, sub: 'kcal total', color: '#ff6b35' },
            { icon: '🥗', label: 'Meals Tracked', value: mealTracked, sub: 'healthy choices', color: '#0099ff' },
            { icon: '⚖️', label: 'BMI', value: bodyMetrics?.bmi?.toFixed(1) || '--', sub: 'body mass index', color: '#ffa502' },
          ].map((stat) => (
            <div
              key={stat.label}
              style={{
                background: '#0d1f35',
                border: '1px solid rgba(0,212,170,0.15)',
                borderRadius: '16px',
                padding: '24px',
                transition: 'all 0.3s',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
                <span style={{ fontSize: '0.75rem', color: '#7a9bb5', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                  {stat.label}
                </span>
                <span style={{ fontSize: '1.3rem' }}>{stat.icon}</span>
              </div>
              <div style={{ fontSize: '2rem', fontFamily: 'Syne, sans-serif', fontWeight: 800, color: stat.color }}>
                {stat.value}
              </div>
              <div style={{ fontSize: '0.8rem', color: '#4a6480', marginTop: '4px' }}>{stat.sub}</div>
            </div>
          ))}
        </div>
      )}

      {/* Body Metrics Tab */}
      {activeTab === 'body' && bodyMetrics && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
          <div
            style={{
              background: '#0d1f35',
              border: '1px solid rgba(0,212,170,0.15)',
              borderRadius: '16px',
              padding: '24px',
            }}
          >
            <h3 style={{ fontFamily: 'Syne, sans-serif', fontWeight: 700, marginBottom: '20px' }}>
              📊 Body Composition
            </h3>
            {[
              { label: 'BMI', value: bodyMetrics.bmi?.toFixed(1), unit: '' },
              { label: 'Body Fat', value: bodyMetrics.bodyFatPercent?.toFixed(1), unit: '%' },
              { label: 'Muscle Mass', value: bodyMetrics.muscleMass?.toFixed(1), unit: 'kg' },
              { label: 'Waist', value: bodyMetrics.waistCircumference?.toFixed(1), unit: 'cm' },
              { label: 'Weight', value: bodyMetrics.weight?.toFixed(1), unit: 'kg' },
              { label: 'Height', value: bodyMetrics.height, unit: 'cm' },
            ].map((m) =>
              m.value ? (
                <div
                  key={m.label}
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    padding: '10px 0',
                    borderBottom: '1px solid rgba(255,255,255,0.05)',
                    fontSize: '0.9rem',
                  }}
                >
                  <span style={{ color: '#7a9bb5' }}>{m.label}</span>
                  <span style={{ fontWeight: 600, color: '#00d4aa' }}>
                    {m.value}
                    {m.unit}
                  </span>
                </div>
              ) : null
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ProgressTracking;
