// HealthAssessment.tsx - Activity 4.2
// 12-question health form covering medical history, allergies, injuries, medications
// Matches the submitAssessmentMutation pattern from screenshots
import { API_BASE_URL } from "../api";
import React, {useEffect, useState } from 'react';

// Assessment questions (12 questions as mentioned in screenshots)
const QUESTIONS = {
  medical_history: [
    { id: 'h1', question: 'Do you have diabetes or blood sugar issues?', key: 'h1' },
    { id: 'h2', question: 'Do you have hypertension or heart conditions?', key: 'h2' },
    { id: 'h3', question: 'Any thyroid disorders?', key: 'h3' },
  ],
  injuries: [
    { id: 'i1', question: 'Any knee or leg injuries?', key: 'i1' },
    { id: 'i2', question: 'Any shoulder or back injuries?', key: 'i2' },
    { id: 'i3', question: 'Any recent surgeries or fractures?', key: 'i3' },
  ],
  allergies: [
    { id: 'a1', question: 'Food allergies (nuts, dairy, gluten)?', key: 'a1' },
    { id: 'a2', question: 'Any medication allergies?', key: 'a2' },
  ],
  medications: [
    { id: 'm1', question: 'Currently on blood pressure medication?', key: 'm1' },
    { id: 'm2', question: 'Taking any supplements or vitamins?', key: 'm2' },
  ],
  lifestyle: [
    { id: 'l1', question: 'Do you smoke or use tobacco products?', key: 'l1' },
    { id: 'l2', question: 'Do you consume alcohol regularly?', key: 'l2' },
  ],
};

const HealthAssessmentForm: React.FC = () => {

  useEffect(() => {
  fetch(`${API_BASE_URL}/`)
    .then(res => res.json())
    .then(data => console.log(data));
}, []);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [step, setStep] = useState<'questions' | 'metrics' | 'results'>('questions');

  const [bodyMetrics, setBodyMetrics] = useState({
    age: '',
    gender: '',
    height: '',
    weight: '',
    bmi: '',
  });

  // Calculate BMI
  const calcBmi = () => {
    const h = parseFloat(bodyMetrics.height) / 100;
    const w = parseFloat(bodyMetrics.weight);
    if (h && w) {
      const bmi = (w / (h * h)).toFixed(1);
      setBodyMetrics((prev) => ({ ...prev, bmi }));
    }
  };

  // Submit assessment mutation (matching screenshot pattern)
  const submitAssessmentMutation = async (assessmentData: any) => {
    setLoading(true);
    try {
      const token = localStorage.getItem('arogyamitra_token');

      // Save body metrics to localStorage (as shown in screenshot)
      localStorage.setItem('body-metrics', JSON.stringify({ ...bodyMetrics, timestamp: new Date().toISOString() }));

      // Submit to backend
      const response = await fetch('https://arogyamitra-o8sd.onrender.com/api/health/assess', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(assessmentData),
      });

      const data = await response.json();

      // Call AI health analysis endpoint (as shown in screenshot)
      try {
        const analysisResponse = await fetch('https://arogyamitra-o8sd.onrender.com/api/health/analyze', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
          body: JSON.stringify({
            age: bodyMetrics.age,
            gender: bodyMetrics.gender,
            height: bodyMetrics.height,
            weight: bodyMetrics.weight,
            bmi: bodyMetrics.bmi,
            medical_history: answers['h1'] || answers['h2'] || answers['h3'] || 'None',
            injuries: answers['i1'] || answers['i2'] || answers['i3'] || 'None',
            fitness_goal: 'general fitness',
          }),
        });
        if (analysisResponse.ok) {
          const aiData = await analysisResponse.json();
          setResult({ ...data, ai_insights: aiData });
        } else {
          setResult(data);
        }
      } catch {
        setResult(data);
      }

      setStep('results');
      alert('✅ Health assessment completed successfully!');
    } catch (error) {
      alert('❌ Failed to submit assessment. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = () => {
    const assessmentData = {
      sleep_hours: 7,
      stress_level: 5,
      water_intake_liters: 2,
      smoking: answers['l1'] === 'yes',
      medical_conditions: [answers['h1'], answers['h2'], answers['h3']].filter(Boolean).join(', ') || null,
    };
    submitAssessmentMutation(assessmentData);
  };

  const allSections = Object.entries(QUESTIONS);
  const totalQuestions = allSections.flatMap(([, qs]) => qs).length;
  const answeredQuestions = Object.keys(answers).length;

  return (
    <div style={{ padding: '32px', maxWidth: '800px' }}>
      <h1
        style={{ fontFamily: 'Syne, sans-serif', fontSize: '1.8rem', fontWeight: 800, marginBottom: '4px', color: '#e8f4f8' }}
      >
        Health Assessment
      </h1>
      <p style={{ color: '#7a9bb5', marginBottom: '24px' }}>
        Complete this 12-question health assessment to help AI build safer, more personalized plans
      </p>

      {step === 'questions' && (
        <>
          {/* Progress Bar */}
          <div
            style={{
              background: 'rgba(255,255,255,0.05)',
              borderRadius: '4px',
              height: '6px',
              marginBottom: '24px',
              overflow: 'hidden',
            }}
          >
            <div
              style={{
                width: `${(answeredQuestions / totalQuestions) * 100}%`,
                height: '100%',
                background: 'linear-gradient(90deg, #00d4aa, #0099ff)',
                transition: 'width 0.3s ease',
              }}
            />
          </div>
          <p style={{ fontSize: '0.85rem', color: '#7a9bb5', marginBottom: '24px' }}>
            {answeredQuestions}/{totalQuestions} questions answered
          </p>

          {allSections.map(([section, questions]) => (
            <div
              key={section}
              style={{
                background: '#0d1f35',
                border: '1px solid rgba(0,212,170,0.15)',
                borderRadius: '16px',
                padding: '24px',
                marginBottom: '16px',
              }}
            >
              <h3
                style={{
                  fontFamily: 'Syne, sans-serif',
                  fontWeight: 700,
                  marginBottom: '16px',
                  fontSize: '1rem',
                  textTransform: 'capitalize',
                  color: '#00d4aa',
                }}
              >
                {section.replace('_', ' ')}
              </h3>
              {questions.map((q) => (
                <div key={q.id} style={{ marginBottom: '14px' }}>
                  <p style={{ fontSize: '0.9rem', marginBottom: '8px', color: '#e8f4f8' }}>{q.question}</p>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    {['yes', 'no', 'sometimes'].map((opt) => (
                      <button
                        key={opt}
                        onClick={() => setAnswers((prev) => ({ ...prev, [q.key]: opt }))}
                        style={{
                          padding: '6px 16px',
                          borderRadius: '8px',
                          border: `1px solid ${answers[q.key] === opt ? '#00d4aa' : 'rgba(0,212,170,0.2)'}`,
                          background: answers[q.key] === opt ? 'rgba(0,212,170,0.15)' : 'transparent',
                          color: answers[q.key] === opt ? '#00d4aa' : '#7a9bb5',
                          cursor: 'pointer',
                          fontFamily: 'inherit',
                          fontSize: '0.85rem',
                          textTransform: 'capitalize',
                          transition: 'all 0.2s',
                        }}
                      >
                        {opt}
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          ))}

          <button
            onClick={() => setStep('metrics')}
            style={{
              background: 'linear-gradient(135deg, #00d4aa, #0099ff)',
              color: '#fff',
              border: 'none',
              padding: '14px 32px',
              borderRadius: '10px',
              fontFamily: 'inherit',
              fontWeight: 600,
              fontSize: '0.9rem',
              cursor: 'pointer',
              width: '100%',
              marginTop: '8px',
            }}
          >
            Next: Body Metrics →
          </button>
        </>
      )}

      {step === 'metrics' && (
        <div
          style={{
            background: '#0d1f35',
            border: '1px solid rgba(0,212,170,0.15)',
            borderRadius: '16px',
            padding: '28px',
          }}
        >
          <h3 style={{ fontFamily: 'Syne, sans-serif', fontWeight: 700, marginBottom: '20px' }}>
            📏 Body Metrics
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
              {[
                { key: 'age', label: 'Age', placeholder: '25', type: 'number' },
                { key: 'gender', label: 'Gender', placeholder: 'male/female', type: 'text' },
                { key: 'height', label: 'Height (cm)', placeholder: '175', type: 'number' },
                { key: 'weight', label: 'Weight (kg)', placeholder: '70', type: 'number' },
              ].map((field) => (
                <div key={field.key}>
                  <label style={{ display: 'block', fontSize: '0.8rem', color: '#7a9bb5', marginBottom: '6px', textTransform: 'uppercase' }}>
                    {field.label}
                  </label>
                  <input
                    type={field.type}
                    placeholder={field.placeholder}
                    value={(bodyMetrics as any)[field.key]}
                    onChange={(e) => {
                      setBodyMetrics((prev) => ({ ...prev, [field.key]: e.target.value }));
                    }}
                    onBlur={calcBmi}
                    style={{
                      width: '100%',
                      background: 'rgba(255,255,255,0.05)',
                      border: '1px solid rgba(0,212,170,0.2)',
                      borderRadius: '10px',
                      padding: '10px 14px',
                      color: '#e8f4f8',
                      fontFamily: 'inherit',
                      fontSize: '0.9rem',
                      outline: 'none',
                    }}
                  />
                </div>
              ))}
            </div>

            {bodyMetrics.bmi && (
              <div
                style={{
                  padding: '12px 16px',
                  background: 'rgba(0,212,170,0.08)',
                  borderRadius: '8px',
                  border: '1px solid rgba(0,212,170,0.2)',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                }}
              >
                <span style={{ color: '#7a9bb5', fontSize: '0.9rem' }}>Calculated BMI</span>
                <span style={{ color: '#00d4aa', fontWeight: 700, fontSize: '1.2rem' }}>{bodyMetrics.bmi}</span>
              </div>
            )}

            <div style={{ display: 'flex', gap: '12px', marginTop: '8px' }}>
              <button
                onClick={() => setStep('questions')}
                style={{
                  flex: 1,
                  background: 'transparent',
                  color: '#00d4aa',
                  border: '1px solid #00d4aa',
                  padding: '14px',
                  borderRadius: '10px',
                  fontFamily: 'inherit',
                  cursor: 'pointer',
                }}
              >
                ← Back
              </button>
              <button
                onClick={handleSubmit}
                disabled={loading}
                style={{
                  flex: 2,
                  background: 'linear-gradient(135deg, #00d4aa, #0099ff)',
                  color: '#fff',
                  border: 'none',
                  padding: '14px',
                  borderRadius: '10px',
                  fontFamily: 'inherit',
                  fontWeight: 600,
                  cursor: loading ? 'not-allowed' : 'pointer',
                  opacity: loading ? 0.7 : 1,
                }}
              >
                {loading ? '⏳ Analyzing...' : '🔍 Submit Assessment'}
              </button>
            </div>
          </div>
        </div>
      )}

      {step === 'results' && result && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div
            style={{
              background: 'linear-gradient(135deg, rgba(0,212,170,0.1), rgba(0,153,255,0.1))',
              border: '1px solid rgba(0,212,170,0.2)',
              borderRadius: '16px',
              padding: '28px',
              textAlign: 'center',
            }}
          >
            <div style={{ fontSize: '3rem', marginBottom: '8px' }}>
              {(result.health_score || 70) >= 80 ? '😊' : (result.health_score || 70) >= 60 ? '😐' : '😟'}
            </div>
            <div
              style={{
                fontFamily: 'Syne, sans-serif',
                fontSize: '3rem',
                fontWeight: 900,
                color: (result.health_score || 70) >= 80 ? '#00d4aa' : '#ffa502',
              }}
            >
              {result.health_score || 75}
            </div>
            <div style={{ color: '#7a9bb5' }}>Health Score</div>
          </div>

          {result.recommendations && (
            <div
              style={{
                background: '#0d1f35',
                border: '1px solid rgba(0,212,170,0.15)',
                borderRadius: '16px',
                padding: '24px',
              }}
            >
              <h3 style={{ fontFamily: 'Syne, sans-serif', fontWeight: 700, marginBottom: '14px' }}>
                💡 Personalized Recommendations
              </h3>
              {(Array.isArray(result.recommendations) ? result.recommendations : [result.recommendations]).map(
                (rec: string, i: number) => (
                  <div
                    key={i}
                    style={{
                      display: 'flex',
                      gap: '8px',
                      padding: '10px',
                      background: 'rgba(0,212,170,0.05)',
                      borderRadius: '8px',
                      marginBottom: '8px',
                      fontSize: '0.9rem',
                      color: '#b0ccd6',
                    }}
                  >
                    <span style={{ color: '#00d4aa', flexShrink: 0 }}>✓</span> {rec}
                  </div>
                )
              )}
            </div>
          )}

          <button
            onClick={() => { setStep('questions'); setAnswers({}); setResult(null); }}
            style={{
              background: 'transparent',
              color: '#00d4aa',
              border: '1px solid #00d4aa',
              padding: '12px',
              borderRadius: '10px',
              fontFamily: 'inherit',
              cursor: 'pointer',
            }}
          >
            🔄 Retake Assessment
          </button>
        </div>
      )}
    </div>
  );
};

export default HealthAssessmentForm;
