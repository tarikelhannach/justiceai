import React from 'react';
import { Link } from '@mui/material';
import { useTranslation } from 'react-i18next';

/**
 * Skip Navigation Component
 * WCAG 2.4.1 (A) - Bypass Blocks
 * Permite a usuarios de teclado/screen readers saltar al contenido principal
 */
const SkipNavigation = () => {
  const { t } = useTranslation();

  return (
    <Link
      href="#main-content"
      sx={{
        position: 'absolute',
        left: '-9999px',
        zIndex: 9999,
        padding: '8px 16px',
        backgroundColor: 'primary.main',
        color: 'primary.contrastText',
        textDecoration: 'none',
        borderRadius: '0 0 4px 0',
        fontWeight: 600,
        fontSize: '1rem',
        '&:focus': {
          left: 0,
          top: 0,
          outline: '3px solid',
          outlineColor: 'secondary.main',
          outlineOffset: '2px',
        },
      }}
      onClick={(e) => {
        e.preventDefault();
        const mainContent = document.getElementById('main-content');
        if (mainContent) {
          mainContent.focus();
          mainContent.scrollIntoView({ behavior: 'smooth' });
        }
      }}
    >
      {t('a11y.skipToMainContent')}
    </Link>
  );
};

export default SkipNavigation;
