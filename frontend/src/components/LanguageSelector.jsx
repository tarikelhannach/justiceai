import React, { useState } from 'react';
import {
  IconButton,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Box,
  Typography,
  useTheme,
  alpha,
} from '@mui/material';
import {
  Language as LanguageIcon,
  Check as CheckIcon,
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';

const languages = [
  {
    code: 'es',
    name: 'Español',
    flag: '🇪🇸',
    dir: 'ltr'
  },
  {
    code: 'fr',
    name: 'Français',
    flag: '🇫🇷',
    dir: 'ltr'
  },
  {
    code: 'ar',
    name: 'العربية',
    flag: '🇲🇦',
    dir: 'rtl'
  }
];

const LanguageSelector = () => {
  const { i18n } = useTranslation();
  const theme = useTheme();
  const [anchorEl, setAnchorEl] = useState(null);
  const open = Boolean(anchorEl);

  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleLanguageChange = (languageCode, dir) => {
    i18n.changeLanguage(languageCode);
    localStorage.setItem('language', languageCode);
    document.documentElement.dir = dir;
    document.documentElement.lang = languageCode;
    handleClose();
  };

  const currentLanguage = languages.find(lang => lang.code === i18n.language) || languages[0];

  return (
    <Box>
      <IconButton
        onClick={handleClick}
        size="small"
        sx={{
          bgcolor: alpha(theme.palette.primary.main, 0.1),
          '&:hover': {
            bgcolor: alpha(theme.palette.primary.main, 0.2),
          },
        }}
      >
        <Typography sx={{ fontSize: '1.2rem', mr: 0.5 }}>
          {currentLanguage.flag}
        </Typography>
        <LanguageIcon fontSize="small" />
      </IconButton>

      <Menu
        anchorEl={anchorEl}
        open={open}
        onClose={handleClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
        PaperProps={{
          sx: {
            mt: 1,
            minWidth: 200,
            borderRadius: 2,
            boxShadow: theme.shadows[8],
          },
        }}
      >
        {languages.map((language) => (
          <MenuItem
            key={language.code}
            onClick={() => handleLanguageChange(language.code, language.dir)}
            selected={i18n.language === language.code}
            sx={{
              py: 1.5,
              px: 2,
              '&:hover': {
                bgcolor: alpha(theme.palette.primary.main, 0.08),
              },
            }}
          >
            <ListItemIcon>
              <Typography sx={{ fontSize: '1.5rem' }}>
                {language.flag}
              </Typography>
            </ListItemIcon>
            <ListItemText
              primary={language.name}
              primaryTypographyProps={{
                fontWeight: i18n.language === language.code ? 600 : 400,
              }}
            />
            {i18n.language === language.code && (
              <CheckIcon color="primary" fontSize="small" sx={{ ml: 1 }} />
            )}
          </MenuItem>
        ))}
      </Menu>
    </Box>
  );
};

export default LanguageSelector;
