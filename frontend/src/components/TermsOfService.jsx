import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  Divider,
  IconButton,
} from '@mui/material';
import { Close as CloseIcon, Gavel as GavelIcon } from '@mui/icons-material';
import { useTranslation } from 'react-i18next';

const TermsOfService = ({ open, onClose, onAccept }) => {
  const { t } = useTranslation();

  return (
    <Dialog 
      open={open} 
      onClose={onClose} 
      maxWidth="md" 
      fullWidth
      aria-labelledby="terms-dialog-title"
      aria-describedby="terms-dialog-description"
    >
      <DialogTitle 
        id="terms-dialog-title"
        sx={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'space-between',
          pb: 1
        }}
      >
        <Box display="flex" alignItems="center" gap={1}>
          <GavelIcon color="primary" />
          <Typography variant="h5" fontWeight={700}>
            {t('legal.termsTitle', 'Términos y Condiciones de Uso')}
          </Typography>
        </Box>
        <IconButton onClick={onClose} size="small" aria-label={t('common.close', 'Cerrar')}>
          <CloseIcon />
        </IconButton>
      </DialogTitle>
      
      <DialogContent dividers id="terms-dialog-description">
        <Box sx={{ '& > *': { mb: 2 } }}>
          {/* Última actualización */}
          <Typography variant="caption" color="text.secondary">
            {t('legal.lastUpdated', 'Última actualización')}: 14 de Octubre, 2025
          </Typography>

          {/* 1. Aceptación */}
          <Box>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              1. {t('legal.acceptance', 'Aceptación de Términos')}
            </Typography>
            <Typography variant="body2" paragraph>
              Al acceder y utilizar el Sistema Judicial Digital de Marruecos, usted acepta cumplir 
              con estos Términos y Condiciones de Uso, todas las leyes y regulaciones aplicables del 
              Reino de Marruecos, y acepta que es responsable del cumplimiento de todas las leyes locales aplicables.
            </Typography>
            <Typography variant="body2" paragraph>
              Si no está de acuerdo con alguno de estos términos, no está autorizado para usar o acceder a este sistema.
            </Typography>
          </Box>

          <Divider />

          {/* 2. Marco Legal */}
          <Box>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              2. {t('legal.legalFramework', 'Marco Legal Aplicable')}
            </Typography>
            <Typography variant="body2" paragraph>
              Este sistema opera bajo las siguientes normativas del Reino de Marruecos:
            </Typography>
            <Typography component="ul" variant="body2" sx={{ pl: 3 }}>
              <li><strong>Ley 09-08</strong>: Protección de Datos Personales (2009)</li>
              <li><strong>Ley 53-05</strong>: Intercambio Electrónico de Datos Jurídicos (2007)</li>
              <li><strong>Dahir 1-11-91</strong>: Constitución de Marruecos (2011) - Artículo 27</li>
              <li><strong>Código de Procedimiento Civil</strong>: Procedimientos judiciales</li>
              <li><strong>Ley 31-08</strong>: Protección del Consumidor</li>
            </Typography>
          </Box>

          <Divider />

          {/* 3. Uso Autorizado */}
          <Box>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              3. {t('legal.authorizedUse', 'Uso Autorizado del Sistema')}
            </Typography>
            <Typography variant="body2" paragraph>
              Este sistema está destinado exclusivamente para:
            </Typography>
            <Typography component="ul" variant="body2" sx={{ pl: 3 }}>
              <li>Gestión de casos judiciales por parte de autoridades competentes</li>
              <li>Consulta de casos por partes involucradas y sus representantes legales</li>
              <li>Presentación y gestión de documentos legales</li>
              <li>Seguimiento del estado de procedimientos judiciales</li>
            </Typography>
            <Typography variant="body2" paragraph color="error.main" fontWeight={600}>
              Queda estrictamente prohibido:
            </Typography>
            <Typography component="ul" variant="body2" sx={{ pl: 3 }} color="error.main">
              <li>Acceso no autorizado o intento de vulnerar la seguridad del sistema</li>
              <li>Uso del sistema para actividades ilegales o fraudulentas</li>
              <li>Compartir credenciales de acceso con terceros</li>
              <li>Modificar, copiar o distribuir contenido sin autorización</li>
              <li>Interferir con el funcionamiento normal del sistema</li>
            </Typography>
          </Box>

          <Divider />

          {/* 4. Cuentas de Usuario */}
          <Box>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              4. {t('legal.userAccounts', 'Cuentas de Usuario y Responsabilidades')}
            </Typography>
            <Typography variant="body2" paragraph>
              Los usuarios son responsables de:
            </Typography>
            <Typography component="ul" variant="body2" sx={{ pl: 3 }}>
              <li>Mantener la confidencialidad de sus credenciales de acceso</li>
              <li>Notificar inmediatamente cualquier uso no autorizado de su cuenta</li>
              <li>Proporcionar información veraz y actualizada</li>
              <li>Cumplir con las políticas de seguridad establecidas</li>
            </Typography>
          </Box>

          <Divider />

          {/* 5. Firma Digital */}
          <Box>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              5. {t('legal.digitalSignature', 'Firma Digital y Validez Legal')}
            </Typography>
            <Typography variant="body2" paragraph>
              De acuerdo con la Ley 53-05 de Intercambio Electrónico de Datos:
            </Typography>
            <Typography component="ul" variant="body2" sx={{ pl: 3 }}>
              <li>Las firmas digitales realizadas en este sistema tienen validez legal equivalente a firmas manuscritas</li>
              <li>Los documentos firmados digitalmente son admisibles como prueba en procedimientos judiciales</li>
              <li>El sistema utiliza certificados digitales emitidos por autoridades certificadoras reconocidas en Marruecos</li>
              <li>Las firmas cualificadas requieren Hardware Security Module (HSM) certificado</li>
            </Typography>
          </Box>

          <Divider />

          {/* 6. Privacidad y Protección de Datos */}
          <Box>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              6. {t('legal.privacy', 'Privacidad y Protección de Datos')}
            </Typography>
            <Typography variant="body2" paragraph>
              El tratamiento de datos personales se rige por:
            </Typography>
            <Typography component="ul" variant="body2" sx={{ pl: 3 }}>
              <li>Ley 09-08 de Protección de Datos Personales</li>
              <li>Nuestra Política de Privacidad detallada</li>
              <li>Directrices de la Comisión Nacional de Control de Protección de Datos Personales (CNDP)</li>
            </Typography>
            <Typography variant="body2" paragraph>
              Los datos se conservan durante 7 años conforme a requisitos legales de retención.
            </Typography>
          </Box>

          <Divider />

          {/* 7. Auditoría y Trazabilidad */}
          <Box>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              7. {t('legal.audit', 'Auditoría y Trazabilidad')}
            </Typography>
            <Typography variant="body2" paragraph>
              El sistema registra todas las acciones realizadas para fines de:
            </Typography>
            <Typography component="ul" variant="body2" sx={{ pl: 3 }}>
              <li>Seguridad y prevención de fraudes</li>
              <li>Cumplimiento normativo y auditorías gubernamentales</li>
              <li>Investigaciones judiciales cuando sea requerido por autoridad competente</li>
            </Typography>
            <Typography variant="body2" paragraph>
              Los registros de auditoría se conservan durante 7 años y son inmutables.
            </Typography>
          </Box>

          <Divider />

          {/* 8. Limitación de Responsabilidad */}
          <Box>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              8. {t('legal.liability', 'Limitación de Responsabilidad')}
            </Typography>
            <Typography variant="body2" paragraph>
              El Gobierno de Marruecos no será responsable por:
            </Typography>
            <Typography component="ul" variant="body2" sx={{ pl: 3 }}>
              <li>Interrupciones del servicio por mantenimiento programado</li>
              <li>Pérdida de datos debido a caso fortuito o fuerza mayor</li>
              <li>Daños indirectos o consecuenciales derivados del uso del sistema</li>
              <li>Decisiones judiciales basadas en la información del sistema (la responsabilidad es del usuario)</li>
            </Typography>
          </Box>

          <Divider />

          {/* 9. Modificaciones */}
          <Box>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              9. {t('legal.modifications', 'Modificaciones a los Términos')}
            </Typography>
            <Typography variant="body2" paragraph>
              Nos reservamos el derecho de modificar estos términos en cualquier momento. Los cambios entrarán 
              en vigor tras su publicación en el sistema. Los usuarios serán notificados de cambios significativos 
              y deberán aceptar los nuevos términos para continuar usando el sistema.
            </Typography>
          </Box>

          <Divider />

          {/* 10. Jurisdicción */}
          <Box>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              10. {t('legal.jurisdiction', 'Jurisdicción y Ley Aplicable')}
            </Typography>
            <Typography variant="body2" paragraph>
              Estos Términos se rigen por las leyes del Reino de Marruecos. Cualquier disputa será resuelta 
              en los tribunales competentes de Marruecos.
            </Typography>
          </Box>

          <Divider />

          {/* 11. Contacto */}
          <Box>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              11. {t('legal.contact', 'Información de Contacto')}
            </Typography>
            <Typography variant="body2" paragraph>
              Para preguntas sobre estos Términos y Condiciones:
            </Typography>
            <Typography variant="body2">
              <strong>Ministerio de Justicia - Reino de Marruecos</strong><br />
              Email: info@justice.gov.ma<br />
              Teléfono: +212 5XX-XXXXXX<br />
              Dirección: Rabat, Marruecos
            </Typography>
          </Box>
        </Box>
      </DialogContent>

      <DialogActions sx={{ p: 2, gap: 1 }}>
        <Button onClick={onClose} variant="outlined">
          {t('common.cancel', 'Cancelar')}
        </Button>
        {onAccept && (
          <Button onClick={onAccept} variant="contained" color="primary">
            {t('legal.accept', 'Aceptar Términos')}
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default TermsOfService;
