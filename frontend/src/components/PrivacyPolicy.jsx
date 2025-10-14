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
  Chip,
} from '@mui/material';
import { 
  Close as CloseIcon, 
  Security as SecurityIcon,
  Shield as ShieldIcon,
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';

const PrivacyPolicy = ({ open, onClose }) => {
  const { t } = useTranslation();

  return (
    <Dialog 
      open={open} 
      onClose={onClose} 
      maxWidth="md" 
      fullWidth
      aria-labelledby="privacy-dialog-title"
      aria-describedby="privacy-dialog-description"
    >
      <DialogTitle 
        id="privacy-dialog-title"
        sx={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'space-between',
          pb: 1
        }}
      >
        <Box display="flex" alignItems="center" gap={1}>
          <ShieldIcon color="primary" />
          <Typography variant="h5" fontWeight={700}>
            {t('legal.privacyTitle', 'Política de Privacidad y Protección de Datos')}
          </Typography>
        </Box>
        <IconButton onClick={onClose} size="small" aria-label={t('common.close', 'Cerrar')}>
          <CloseIcon />
        </IconButton>
      </DialogTitle>
      
      <DialogContent dividers id="privacy-dialog-description">
        <Box sx={{ '& > *': { mb: 2 } }}>
          {/* Última actualización */}
          <Box display="flex" gap={1} alignItems="center" mb={2}>
            <Typography variant="caption" color="text.secondary">
              {t('legal.lastUpdated', 'Última actualización')}: 14 de Octubre, 2025
            </Typography>
            <Chip label="Ley 09-08" size="small" color="primary" variant="outlined" />
            <Chip label="CNDP" size="small" color="primary" variant="outlined" />
          </Box>

          {/* Introducción */}
          <Box>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              {t('legal.introduction', 'Introducción')}
            </Typography>
            <Typography variant="body2" paragraph>
              El Ministerio de Justicia del Reino de Marruecos se compromete a proteger la privacidad y 
              seguridad de los datos personales de todos los usuarios del Sistema Judicial Digital. Esta 
              Política de Privacidad describe cómo recopilamos, usamos, almacenamos y protegemos su información 
              personal de acuerdo con la <strong>Ley 09-08 de Protección de Datos Personales</strong> y las 
              directrices de la Comisión Nacional de Control de Protección de Datos Personales (CNDP).
            </Typography>
          </Box>

          <Divider />

          {/* 1. Responsable del Tratamiento */}
          <Box>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              1. {t('legal.dataController', 'Responsable del Tratamiento de Datos')}
            </Typography>
            <Typography variant="body2" paragraph>
              <strong>Entidad:</strong> Ministerio de Justicia del Reino de Marruecos<br />
              <strong>Dirección:</strong> Rabat, Marruecos<br />
              <strong>Email:</strong> dpo@justice.gov.ma<br />
              <strong>Registro CNDP:</strong> [Número de registro]
            </Typography>
          </Box>

          <Divider />

          {/* 2. Datos que Recopilamos */}
          <Box>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              2. {t('legal.dataCollected', 'Datos Personales que Recopilamos')}
            </Typography>
            <Typography variant="body2" paragraph fontWeight={600}>
              2.1. Datos de Identificación:
            </Typography>
            <Typography component="ul" variant="body2" sx={{ pl: 3 }}>
              <li>Nombre completo</li>
              <li>Número de documento de identidad (CNI/Pasaporte)</li>
              <li>Fecha de nacimiento</li>
              <li>Dirección postal y electrónica</li>
              <li>Número de teléfono</li>
            </Typography>

            <Typography variant="body2" paragraph fontWeight={600} sx={{ mt: 2 }}>
              2.2. Datos Profesionales (según rol):
            </Typography>
            <Typography component="ul" variant="body2" sx={{ pl: 3 }}>
              <li>Número de colegiación (abogados)</li>
              <li>Número de matrícula judicial (jueces)</li>
              <li>Cargo y dependencia (funcionarios)</li>
            </Typography>

            <Typography variant="body2" paragraph fontWeight={600} sx={{ mt: 2 }}>
              2.3. Datos de Casos Judiciales:
            </Typography>
            <Typography component="ul" variant="body2" sx={{ pl: 3 }}>
              <li>Número de expediente</li>
              <li>Tipo de procedimiento</li>
              <li>Documentos presentados</li>
              <li>Estado procesal</li>
            </Typography>

            <Typography variant="body2" paragraph fontWeight={600} sx={{ mt: 2 }}>
              2.4. Datos Técnicos:
            </Typography>
            <Typography component="ul" variant="body2" sx={{ pl: 3 }}>
              <li>Dirección IP</li>
              <li>Navegador y dispositivo</li>
              <li>Fecha y hora de acceso</li>
              <li>Acciones realizadas en el sistema</li>
            </Typography>
          </Box>

          <Divider />

          {/* 3. Finalidad del Tratamiento */}
          <Box>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              3. {t('legal.dataPurpose', 'Finalidad del Tratamiento de Datos')}
            </Typography>
            <Typography variant="body2" paragraph>
              Sus datos personales son tratados para las siguientes finalidades legítimas:
            </Typography>
            <Typography component="ul" variant="body2" sx={{ pl: 3 }}>
              <li><strong>Gestión judicial:</strong> Tramitación de casos y procedimientos judiciales</li>
              <li><strong>Autenticación:</strong> Verificación de identidad y control de acceso</li>
              <li><strong>Comunicaciones:</strong> Notificaciones sobre el estado de casos</li>
              <li><strong>Seguridad:</strong> Prevención de fraudes y accesos no autorizados</li>
              <li><strong>Cumplimiento legal:</strong> Auditorías y requerimientos judiciales</li>
              <li><strong>Mejora del servicio:</strong> Análisis estadísticos anónimos</li>
            </Typography>
          </Box>

          <Divider />

          {/* 4. Base Legal */}
          <Box>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              4. {t('legal.legalBasis', 'Base Legal del Tratamiento')}
            </Typography>
            <Typography variant="body2" paragraph>
              El tratamiento de datos se fundamenta en:
            </Typography>
            <Typography component="ul" variant="body2" sx={{ pl: 3 }}>
              <li><strong>Obligación legal:</strong> Cumplimiento de normativas judiciales (Art. 5 Ley 09-08)</li>
              <li><strong>Ejercicio de autoridad pública:</strong> Administración de justicia</li>
              <li><strong>Consentimiento:</strong> Para comunicaciones no esenciales</li>
              <li><strong>Interés legítimo:</strong> Seguridad del sistema y prevención de fraudes</li>
            </Typography>
          </Box>

          <Divider />

          {/* 5. Conservación de Datos */}
          <Box>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              5. {t('legal.dataRetention', 'Conservación y Retención de Datos')}
            </Typography>
            <Typography variant="body2" paragraph>
              Los datos se conservan durante los siguientes períodos:
            </Typography>
            <Box sx={{ bgcolor: 'action.hover', p: 2, borderRadius: 1, mb: 2 }}>
              <Typography variant="body2" fontWeight={600} gutterBottom>
                Períodos de Retención:
              </Typography>
              <Typography component="ul" variant="body2" sx={{ pl: 3, mb: 0 }}>
                <li><strong>Datos de casos:</strong> 7 años desde cierre (requisito legal)</li>
                <li><strong>Registros de auditoría:</strong> 7 años (inmutables)</li>
                <li><strong>Datos de usuario inactivo:</strong> 1 año sin actividad</li>
                <li><strong>Archivos temporales:</strong> 30 días</li>
                <li><strong>Backups:</strong> 90 días</li>
              </Typography>
            </Box>
            <Typography variant="body2" paragraph>
              Tras estos períodos, los datos son eliminados o anonimizados de forma segura e irreversible.
            </Typography>
          </Box>

          <Divider />

          {/* 6. Seguridad de Datos */}
          <Box>
            <Typography variant="h6" fontWeight={600} gutterBottom display="flex" alignItems="center" gap={1}>
              <SecurityIcon color="primary" fontSize="small" />
              6. {t('legal.dataSecurity', 'Medidas de Seguridad')}
            </Typography>
            <Typography variant="body2" paragraph>
              Implementamos medidas técnicas y organizativas de alto nivel:
            </Typography>
            <Typography variant="body2" paragraph fontWeight={600}>
              Seguridad Técnica:
            </Typography>
            <Typography component="ul" variant="body2" sx={{ pl: 3 }}>
              <li>Encriptación TLS 1.3 en tránsito</li>
              <li>Encriptación AES-256 en reposo</li>
              <li>Autenticación multifactor (2FA)</li>
              <li>Hardware Security Module (HSM) para firmas digitales</li>
              <li>Firewalls y sistemas de detección de intrusiones</li>
              <li>Backups automáticos encriptados</li>
            </Typography>

            <Typography variant="body2" paragraph fontWeight={600} sx={{ mt: 2 }}>
              Seguridad Organizativa:
            </Typography>
            <Typography component="ul" variant="body2" sx={{ pl: 3 }}>
              <li>Control de acceso basado en roles (RBAC)</li>
              <li>Auditorías de seguridad periódicas</li>
              <li>Formación continua del personal</li>
              <li>Protocolo de respuesta a incidentes</li>
            </Typography>
          </Box>

          <Divider />

          {/* 7. Derechos de los Usuarios */}
          <Box>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              7. {t('legal.userRights', 'Sus Derechos (Art. 8 Ley 09-08)')}
            </Typography>
            <Typography variant="body2" paragraph>
              Usted tiene los siguientes derechos sobre sus datos personales:
            </Typography>
            
            <Box sx={{ bgcolor: 'primary.main', color: 'primary.contrastText', p: 2, borderRadius: 1, mb: 2 }}>
              <Typography variant="body2" fontWeight={600} gutterBottom>
                ✓ Derechos Fundamentales:
              </Typography>
              <Typography component="ul" variant="body2" sx={{ pl: 3, mb: 0 }}>
                <li><strong>Acceso:</strong> Obtener copia de sus datos (API: /api/users/me/data)</li>
                <li><strong>Rectificación:</strong> Corregir datos inexactos (Configuración → Perfil)</li>
                <li><strong>Supresión:</strong> Solicitar eliminación de datos (sujeto a obligaciones legales)</li>
                <li><strong>Oposición:</strong> Oponerse al tratamiento para fines específicos</li>
                <li><strong>Portabilidad:</strong> Recibir datos en formato estructurado (JSON/CSV)</li>
                <li><strong>Limitación:</strong> Restringir el tratamiento en ciertos casos</li>
              </Typography>
            </Box>

            <Typography variant="body2" paragraph>
              <strong>Ejercicio de derechos:</strong> Envíe solicitud a dpo@justice.gov.ma con copia de su 
              documento de identidad. Responderemos en un plazo máximo de 30 días.
            </Typography>
          </Box>

          <Divider />

          {/* 8. Transferencias Internacionales */}
          <Box>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              8. {t('legal.dataTransfers', 'Transferencias Internacionales')}
            </Typography>
            <Typography variant="body2" paragraph>
              <strong>Principio general:</strong> Los datos personales se almacenan y procesan exclusivamente 
              en servidores ubicados en Marruecos.
            </Typography>
            <Typography variant="body2" paragraph>
              <strong>Excepciones:</strong> Transferencias internacionales solo se realizan cuando:
            </Typography>
            <Typography component="ul" variant="body2" sx={{ pl: 3 }}>
              <li>Exista decisión de adecuación de la CNDP</li>
              <li>Se implementen cláusulas contractuales tipo aprobadas</li>
              <li>Sea requerido por autoridad judicial competente</li>
              <li>Exista consentimiento explícito del interesado</li>
            </Typography>
          </Box>

          <Divider />

          {/* 9. Cookies y Tecnologías Similares */}
          <Box>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              9. {t('legal.cookies', 'Cookies y Tecnologías de Seguimiento')}
            </Typography>
            <Typography variant="body2" paragraph>
              Utilizamos cookies estrictamente necesarias para:
            </Typography>
            <Typography component="ul" variant="body2" sx={{ pl: 3 }}>
              <li>Mantener sesión de usuario (JWT tokens)</li>
              <li>Preferencias de idioma y tema</li>
              <li>Seguridad y prevención de fraudes (CSRF tokens)</li>
            </Typography>
            <Typography variant="body2" paragraph>
              <strong>No utilizamos:</strong> Cookies de publicidad, seguimiento de terceros o perfilado.
            </Typography>
          </Box>

          <Divider />

          {/* 10. Notificación de Brechas */}
          <Box>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              10. {t('legal.breachNotification', 'Notificación de Brechas de Seguridad')}
            </Typography>
            <Typography variant="body2" paragraph>
              En caso de brecha de seguridad que afecte sus datos:
            </Typography>
            <Typography component="ul" variant="body2" sx={{ pl: 3 }}>
              <li>Notificaremos a la CNDP en un plazo de 72 horas</li>
              <li>Le informaremos directamente si existe alto riesgo para sus derechos</li>
              <li>Implementaremos medidas correctivas inmediatas</li>
              <li>Publicaremos informe transparente sobre el incidente</li>
            </Typography>
          </Box>

          <Divider />

          {/* 11. Cambios a la Política */}
          <Box>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              11. {t('legal.policyChanges', 'Cambios a esta Política')}
            </Typography>
            <Typography variant="body2" paragraph>
              Nos reservamos el derecho de actualizar esta política. Los cambios significativos serán 
              notificados mediante:
            </Typography>
            <Typography component="ul" variant="body2" sx={{ pl: 3 }}>
              <li>Notificación por email</li>
              <li>Aviso destacado en el sistema</li>
              <li>Requerimiento de nueva aceptación si es necesario</li>
            </Typography>
          </Box>

          <Divider />

          {/* 12. Contacto y Reclamaciones */}
          <Box>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              12. {t('legal.complaints', 'Contacto y Reclamaciones')}
            </Typography>
            <Typography variant="body2" paragraph>
              <strong>Delegado de Protección de Datos (DPO):</strong><br />
              Email: dpo@justice.gov.ma<br />
              Teléfono: +212 5XX-XXXXXX
            </Typography>
            <Typography variant="body2" paragraph>
              <strong>Autoridad de Control (CNDP):</strong><br />
              Si no está satisfecho con nuestra respuesta, puede presentar reclamación ante:<br />
              <strong>Commission Nationale de Contrôle de la Protection des Données à Caractère Personnel</strong><br />
              Website: www.cndp.ma<br />
              Email: contact@cndp.ma
            </Typography>
          </Box>
        </Box>
      </DialogContent>

      <DialogActions sx={{ p: 2 }}>
        <Button onClick={onClose} variant="contained">
          {t('common.close', 'Cerrar')}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default PrivacyPolicy;
