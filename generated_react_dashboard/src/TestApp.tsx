import React from 'react';

export default function TestApp() {
  console.log('TestApp component is rendering');

  return (
    <div style={{ padding: '20px', backgroundColor: '#f0f0f0', minHeight: '100vh' }}>
      <h1>React Dashboard Test</h1>
      <p>If you can see this, React is working!</p>
      <p>Current time: {new Date().toLocaleString()}</p>
      <div style={{ marginTop: '20px', padding: '10px', backgroundColor: 'white', border: '1px solid #ccc' }}>
        <h2>Debug Information:</h2>
        <ul>
          <li>React version: {React.version}</li>
          <li>Window location: {window.location.href}</li>
          <li>API endpoint would be: http://localhost:8000/api/pipelines</li>
        </ul>
      </div>
    </div>
  );
}