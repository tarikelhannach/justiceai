import React, { useState, useEffect } from 'react';
import {
  Box,
  TextField,
  IconButton,
  InputAdornment,
  Paper,
  Popper,
  ClickAwayListener,
  List,
  ListItem,
  ListItemText,
  Typography,
  Chip,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  Grid,
  Button,
  Collapse
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import FilterListIcon from '@mui/icons-material/FilterList';
import ClearIcon from '@mui/icons-material/Clear';
import { useTranslation } from 'react-i18next';
import api from '../services/api';

const SearchBar = ({ onSearchResults }) => {
  const { t } = useTranslation();
  const [searchQuery, setSearchQuery] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState({
    status: '',
    startDate: '',
    endDate: ''
  });
  const [anchorEl, setAnchorEl] = useState(null);
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(false);

  // Debounce search
  useEffect(() => {
    if (searchQuery.length > 2) {
      const timer = setTimeout(() => {
        handleSearch();
      }, 500);
      return () => clearTimeout(timer);
    } else if (searchQuery.length === 0) {
      setSuggestions([]);
      setAnchorEl(null);
    }
  }, [searchQuery]);

  const handleSearch = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      
      if (searchQuery) params.append('query', searchQuery);
      if (filters.status) params.append('status', filters.status);
      if (filters.startDate) params.append('start_date', filters.startDate);
      if (filters.endDate) params.append('end_date', filters.endDate);

      const response = await api.get(`/cases/search/?${params.toString()}`);
      setSuggestions(response.data);
      
      if (onSearchResults) {
        onSearchResults(response.data);
      }
      
      if (response.data.length > 0 && searchQuery) {
        setAnchorEl(document.getElementById('search-input'));
      }
    } catch (error) {
      console.error('Error searching cases:', error);
      setSuggestions([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectCase = (caseItem) => {
    setSearchQuery('');
    setSuggestions([]);
    setAnchorEl(null);
    if (onSearchResults) {
      onSearchResults([caseItem]);
    }
  };

  const handleClearSearch = () => {
    setSearchQuery('');
    setFilters({ status: '', startDate: '', endDate: '' });
    setSuggestions([]);
    setAnchorEl(null);
    if (onSearchResults) {
      onSearchResults(null);
    }
  };

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({ ...prev, [field]: value }));
  };

  const handleApplyFilters = () => {
    handleSearch();
    setShowFilters(false);
  };

  const getStatusColor = (status) => {
    const colors = {
      pending: 'warning',
      in_progress: 'info',
      under_review: 'secondary',
      resolved: 'success',
      closed: 'default'
    };
    return colors[status] || 'default';
  };

  const hasActiveFilters = filters.status || filters.startDate || filters.endDate;

  return (
    <Box sx={{ width: '100%', mb: 3 }}>
      <Box sx={{ display: 'flex', gap: 1 }}>
        <TextField
          id="search-input"
          fullWidth
          placeholder={t('search.placeholder')}
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          onKeyPress={(e) => {
            if (e.key === 'Enter') {
              handleSearch();
            }
          }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
            endAdornment: searchQuery && (
              <InputAdornment position="end">
                <IconButton size="small" onClick={handleClearSearch}>
                  <ClearIcon />
                </IconButton>
              </InputAdornment>
            )
          }}
          sx={{
            '& .MuiOutlinedInput-root': {
              borderRadius: 3,
              backgroundColor: 'background.paper'
            }
          }}
        />
        <IconButton
          onClick={() => setShowFilters(!showFilters)}
          sx={{
            borderRadius: 3,
            backgroundColor: hasActiveFilters ? 'primary.main' : 'background.paper',
            color: hasActiveFilters ? 'white' : 'text.primary',
            '&:hover': {
              backgroundColor: hasActiveFilters ? 'primary.dark' : 'action.hover'
            }
          }}
        >
          <FilterListIcon />
        </IconButton>
      </Box>

      {/* Advanced Filters */}
      <Collapse in={showFilters}>
        <Paper sx={{ mt: 2, p: 2, borderRadius: 3 }}>
          <Typography variant="subtitle2" gutterBottom>
            {t('search.advancedFilters')}
          </Typography>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={4}>
              <FormControl fullWidth size="small">
                <InputLabel>{t('cases.status.title')}</InputLabel>
                <Select
                  value={filters.status}
                  onChange={(e) => handleFilterChange('status', e.target.value)}
                  label={t('cases.status.title')}
                >
                  <MenuItem value="">{t('common.all')}</MenuItem>
                  <MenuItem value="pending">{t('cases.status.pending')}</MenuItem>
                  <MenuItem value="in_progress">{t('cases.status.inProgress')}</MenuItem>
                  <MenuItem value="under_review">{t('cases.status.underReview')}</MenuItem>
                  <MenuItem value="resolved">{t('cases.status.resolved')}</MenuItem>
                  <MenuItem value="closed">{t('cases.status.closed')}</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                size="small"
                type="date"
                label={t('search.startDate')}
                value={filters.startDate}
                onChange={(e) => handleFilterChange('startDate', e.target.value)}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                size="small"
                type="date"
                label={t('search.endDate')}
                value={filters.endDate}
                onChange={(e) => handleFilterChange('endDate', e.target.value)}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
          </Grid>
          <Box sx={{ mt: 2, display: 'flex', gap: 1, justifyContent: 'flex-end' }}>
            <Button onClick={() => setShowFilters(false)}>
              {t('common.cancel')}
            </Button>
            <Button variant="contained" onClick={handleApplyFilters}>
              {t('search.applyFilters')}
            </Button>
          </Box>
        </Paper>
      </Collapse>

      {/* Search Suggestions */}
      <Popper
        open={Boolean(anchorEl) && suggestions.length > 0}
        anchorEl={anchorEl}
        placement="bottom-start"
        style={{ zIndex: 1300, width: anchorEl ? anchorEl.offsetWidth : undefined }}
      >
        <ClickAwayListener onClickAway={() => setAnchorEl(null)}>
          <Paper sx={{ mt: 1, maxHeight: 400, overflow: 'auto', borderRadius: 2 }}>
            <List>
              {suggestions.map((caseItem) => (
                <ListItem
                  key={caseItem.id}
                  button
                  onClick={() => handleSelectCase(caseItem)}
                  sx={{
                    '&:hover': {
                      backgroundColor: 'action.hover'
                    }
                  }}
                >
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography variant="body2" fontWeight="bold">
                          {caseItem.case_number}
                        </Typography>
                        <Chip
                          label={t(`cases.status.${caseItem.status}`)}
                          size="small"
                          color={getStatusColor(caseItem.status)}
                        />
                      </Box>
                    }
                    secondary={
                      <React.Fragment>
                        <Typography variant="body2" component="span">
                          {caseItem.title}
                        </Typography>
                        <br />
                        <Typography variant="caption" color="text.secondary">
                          {t('cases.owner')}: {caseItem.owner.name}
                        </Typography>
                      </React.Fragment>
                    }
                  />
                </ListItem>
              ))}
            </List>
          </Paper>
        </ClickAwayListener>
      </Popper>
    </Box>
  );
};

export default SearchBar;
