import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './utils/clearCache'; // 导入清空缓存工具，使其在 window 对象上可用

const rootElement = document.getElementById('root');
if (!rootElement) {
  throw new Error("Could not find root element to mount to");
}

const root = ReactDOM.createRoot(rootElement);
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);