import React from 'react';
import ReactDOM from 'react-dom/client';
import '@fontsource/source-sans-3/latin-400.css';
import '@fontsource/source-sans-3/latin-600.css';
import '@fontsource/source-code-pro/latin-400.css';
import '@fontsource/source-code-pro/latin-600.css';
import { ReportWorkspace } from './report_workspace';
import './design_tokens.css';
import './report_layout.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ReportWorkspace />
  </React.StrictMode>,
);
