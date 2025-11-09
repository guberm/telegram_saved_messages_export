import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Typography,
  Button,
  Box,
  CircularProgress,
  Alert,
  Card,
  CardContent,
  Grid,
  LinearProgress,
  FormControlLabel,
  Checkbox,
} from '@mui/material';
import {
  CloudDownload,
  Assessment,
  Folder,
  CheckCircle,
} from '@mui/icons-material';
import axios from 'axios';

function App() {
  const [status, setStatus] = useState('idle');
  const [stats, setStats] = useState(null);
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [isPolling, setIsPolling] = useState(false);
  const [forceReexport, setForceReexport] = useState(false);
  const [logs, setLogs] = useState([]);

  // Add log entry
  const addLog = (message, type = 'info') => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs(prev => [...prev, { timestamp, message, type }]);
    console.log(`[${timestamp}] ${type.toUpperCase()}: ${message}`);
  };

  // Fetch stats on load
  useEffect(() => {
    addLog('Application started', 'info');
    fetchStats();
  }, []);

  // Poll export status when export is running
  useEffect(() => {
    let interval;
    if (isPolling) {
      addLog('Starting export status polling', 'info');
      interval = setInterval(async () => {
        try {
          const response = await axios.get('/api/export/status');
          const exportStatus = response.data;
          
          console.log('Export status:', exportStatus);
          
          setMessage(exportStatus.message || 'Exporting...');
          setProgress(exportStatus.progress || 0);
          
          if (!exportStatus.running) {
            // Export completed or failed
            setIsPolling(false);
            if (exportStatus.error) {
              addLog(`Export failed: ${exportStatus.error}`, 'error');
              setError(exportStatus.error);
              setStatus('error');
            } else {
              addLog('Export completed successfully!', 'success');
              setStatus('completed');
              fetchStats();
            }
          } else {
            addLog(`Progress: ${exportStatus.progress}% - ${exportStatus.message}`, 'info');
          }
        } catch (err) {
          console.error('Failed to fetch export status:', err);
          addLog(`Failed to fetch status: ${err.message}`, 'error');
        }
      }, 2000); // Poll every 2 seconds
    }
    
    return () => {
      if (interval) {
        clearInterval(interval);
        addLog('Stopped export status polling', 'info');
      }
    };
  }, [isPolling]);

  const fetchStats = async () => {
    try {
      addLog('Fetching stats...', 'info');
      const response = await axios.get('/api/stats');
      console.log('Stats response:', response.data);
      setStats(response.data);
      addLog(`Stats loaded: ${response.data.total_messages} messages`, 'success');
    } catch (err) {
      console.error('Failed to fetch stats:', err);
      addLog(`Failed to fetch stats: ${err.message}`, 'error');
    }
  };

  const startExport = async () => {
    setStatus('running');
    setError('');
    setMessage('Starting export...');
    setProgress(0);
    
    addLog(`Starting export (force_reexport=${forceReexport})...`, 'info');

    try {
      const url = `/api/export/start?force_reexport=${forceReexport}`;
      addLog(`POST ${url}`, 'info');
      const response = await axios.post(url);
      console.log('Export start response:', response.data);
      
      if (response.data.status === 'success') {
        addLog('Export started successfully', 'success');
        setIsPolling(true); // Start polling for status
      }
    } catch (err) {
      console.error('Export start error:', err);
      const errorMsg = err.response?.data?.detail || err.response?.data?.message || 'Export failed';
      addLog(`Export start failed: ${errorMsg}`, 'error');
      setError(errorMsg);
      setStatus('error');
    }
  };

  const openOutputFolder = async () => {
    try {
      addLog('Opening output folder...', 'info');
      await axios.post('/api/open-folder');
      addLog('Output folder opened', 'success');
    } catch (err) {
      console.error('Failed to open folder:', err);
      addLog(`Failed to open folder: ${err.message}`, 'error');
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Paper elevation={3} sx={{ p: 4, mb: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom align="center">
          📱 Telegram Messages Exporter
        </Typography>
        <Typography variant="subtitle1" align="center" color="text.secondary" paragraph>
          Export your Telegram saved messages to HTML and Markdown files
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
            {error}
          </Alert>
        )}

        {message && status !== 'error' && (
          <Alert severity="info" sx={{ mb: 2 }}>
            {message}
          </Alert>
        )}

        {/* Export Options */}
        <Box sx={{ mb: 3 }}>
          <FormControlLabel
            control={
              <Checkbox
                checked={forceReexport}
                onChange={(e) => setForceReexport(e.target.checked)}
                disabled={status === 'running'}
              />
            }
            label="Force re-export (re-export already exported messages)"
          />
        </Box>

        {/* Stats Cards */}
        {stats && (
          <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center" mb={1}>
                    <Assessment color="primary" sx={{ mr: 1 }} />
                    <Typography variant="h6">Total Messages</Typography>
                  </Box>
                  <Typography variant="h4">{stats.total_messages || 0}</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center" mb={1}>
                    <CheckCircle color="success" sx={{ mr: 1 }} />
                    <Typography variant="h6">Exported</Typography>
                  </Box>
                  <Typography variant="h4">{stats.exported_messages || 0}</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center" mb={1}>
                    <Folder color="action" sx={{ mr: 1 }} />
                    <Typography variant="h6">Export Sessions</Typography>
                  </Box>
                  <Typography variant="h4">{stats.export_sessions || 0}</Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}

        {/* Export Controls */}
        <Box display="flex" justifyContent="center" gap={2} flexWrap="wrap">
          <Button
            variant="contained"
            size="large"
            startIcon={status === 'running' ? <CircularProgress size={20} color="inherit" /> : <CloudDownload />}
            onClick={startExport}
            disabled={status === 'running'}
          >
            {status === 'running' ? 'Exporting...' : 'Start Export'}
          </Button>
          
          <Button
            variant="outlined"
            size="large"
            startIcon={<Folder />}
            onClick={openOutputFolder}
          >
            Open Export Folder
          </Button>
        </Box>

        {status === 'running' && (
          <Box sx={{ mt: 3 }}>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
              {message}
            </Typography>
            <LinearProgress variant="determinate" value={progress} />
            <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
              {progress}% complete
            </Typography>
          </Box>
        )}

        {status === 'completed' && (
          <Alert severity="success" sx={{ mt: 3 }}>
            Export completed successfully! Check the output folder for your exported messages.
          </Alert>
        )}
      </Paper>

      <Paper elevation={2} sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          About This Tool
        </Typography>
        <Typography variant="body2" paragraph>
          This tool exports your Telegram saved messages into organized HTML and Markdown files.
          Each message is saved with its content, media, and metadata.
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Features: Incremental exports • Media handling • Database tracking • Multiple export formats
        </Typography>
      </Paper>

      {/* Logs Panel */}
      <Paper elevation={2} sx={{ p: 3, mt: 2 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">
            Activity Log
          </Typography>
          <Button size="small" onClick={() => setLogs([])}>
            Clear Log
          </Button>
        </Box>
        <Box 
          sx={{ 
            maxHeight: 300, 
            overflow: 'auto', 
            bgcolor: '#f5f5f5', 
            p: 2, 
            borderRadius: 1,
            fontFamily: 'monospace',
            fontSize: '0.875rem'
          }}
        >
          {logs.length === 0 ? (
            <Typography variant="body2" color="text.secondary">No activity yet...</Typography>
          ) : (
            logs.map((log, index) => (
              <Box 
                key={index} 
                sx={{ 
                  mb: 0.5,
                  color: log.type === 'error' ? 'error.main' : 
                         log.type === 'success' ? 'success.main' : 
                         'text.primary'
                }}
              >
                <span style={{ opacity: 0.7 }}>[{log.timestamp}]</span> {log.message}
              </Box>
            ))
          )}
        </Box>
      </Paper>
    </Container>
  );
}

export default App;
