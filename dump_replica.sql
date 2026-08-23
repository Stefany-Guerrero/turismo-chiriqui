/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19-11.4.12-MariaDB, for Win64 (AMD64)
--
-- Host: localhost    Database: turismo_chiriqui
-- ------------------------------------------------------
-- Server version	11.4.12-MariaDB-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*M!100616 SET @OLD_NOTE_VERBOSITY=@@NOTE_VERBOSITY, NOTE_VERBOSITY=0 */;

--
-- Table structure for table `clientes`
--

DROP TABLE IF EXISTS `clientes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `clientes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `direccion` varchar(200) DEFAULT NULL,
  `fecha_registro` datetime DEFAULT NULL,
  `usuario_id` int(11) DEFAULT NULL,
  `fecha_creacion` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  KEY `usuario_id` (`usuario_id`),
  CONSTRAINT `clientes_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `clientes`
--

LOCK TABLES `clientes` WRITE;
/*!40000 ALTER TABLE `clientes` DISABLE KEYS */;
INSERT INTO `clientes` VALUES
(1,'Stefany Guerrero','stefanyrachel11@gmail.com','+507 6330-1291',NULL,NULL,2,'2026-07-07 17:53:57'),
(2,'Administrador','admin@turismo.com','7890-7890',NULL,NULL,1,'2026-07-07 21:10:54');
/*!40000 ALTER TABLE `clientes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `disponibilidad`
--

DROP TABLE IF EXISTS `disponibilidad`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `disponibilidad` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `servicio_id` int(11) NOT NULL,
  `fecha` date NOT NULL,
  `cupos_disponibles` int(11) DEFAULT 0,
  `fecha_actualizacion` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `servicio_id` (`servicio_id`,`fecha`),
  CONSTRAINT `disponibilidad_ibfk_1` FOREIGN KEY (`servicio_id`) REFERENCES `servicios` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `disponibilidad`
--

LOCK TABLES `disponibilidad` WRITE;
/*!40000 ALTER TABLE `disponibilidad` DISABLE KEYS */;
INSERT INTO `disponibilidad` VALUES
(1,1,'2026-07-16',19,'2026-07-07 19:15:58'),
(2,5,'2026-07-15',11,'2026-07-07 21:10:54'),
(3,3,'2026-07-16',14,'2026-07-07 21:24:26'),
(4,6,'2026-07-24',19,'2026-07-08 02:02:05'),
(5,6,'2026-07-25',19,'2026-07-08 02:02:05'),
(6,6,'2026-07-26',19,'2026-07-08 02:02:05'),
(7,4,'2026-07-19',9,'2026-07-08 03:16:52'),
(8,1,'2026-07-22',19,'2026-07-08 03:35:21'),
(9,7,'2026-07-16',29,'2026-07-08 03:43:31'),
(10,12,'2026-07-18',9,'2026-07-08 03:51:09'),
(11,12,'2026-07-19',9,'2026-07-08 03:51:09'),
(12,7,'2026-07-17',29,'2026-07-08 03:54:49'),
(17,9,'2026-07-17',14,'2026-07-08 04:13:43'),
(18,3,'2026-07-17',11,'2026-07-09 02:00:07'),
(19,12,'2026-07-11',9,'2026-07-09 03:06:12'),
(20,12,'2026-07-12',9,'2026-07-09 03:06:12');
/*!40000 ALTER TABLE `disponibilidad` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notificaciones`
--

DROP TABLE IF EXISTS `notificaciones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `notificaciones` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `usuario_id` int(11) NOT NULL,
  `titulo` varchar(200) NOT NULL,
  `mensaje` text DEFAULT NULL,
  `tipo` varchar(50) DEFAULT NULL,
  `referencia_id` int(11) DEFAULT NULL,
  `referencia_tipo` varchar(50) DEFAULT NULL,
  `leido` tinyint(1) DEFAULT NULL,
  `fecha_creacion` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `usuario_id` (`usuario_id`),
  CONSTRAINT `notificaciones_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notificaciones`
--

LOCK TABLES `notificaciones` WRITE;
/*!40000 ALTER TABLE `notificaciones` DISABLE KEYS */;
INSERT INTO `notificaciones` VALUES
(1,1,'Cotización recibida','Tu solicitud #14 tiene una cotización de B/.65.00.','cotizada',14,'solicitud',1,'2026-07-10 01:14:03'),
(2,1,'Cotización recibida','Tu solicitud #14 tiene una cotización de B/.65.00.','cotizada',14,'solicitud',1,'2026-07-10 01:14:15'),
(3,2,'Cotización recibida','Tu solicitud #15 tiene una cotización de B/.65.00.','cotizada',15,'solicitud',1,'2026-07-10 01:20:18'),
(4,2,'Solicitud aprobada','Tu solicitud #15 ha sido aprobada. ¡Viaje confirmado!','aprobada',15,'solicitud',0,'2026-07-10 01:57:05'),
(5,1,'Cotización recibida','Tu solicitud #14 tiene una cotización de B/.130.00.','cotizada',14,'solicitud',1,'2026-07-10 02:04:06'),
(6,1,'Solicitud aprobada','Tu solicitud #14 ha sido aprobada. ¡Viaje confirmado!','aprobada',14,'solicitud',1,'2026-07-10 02:04:14');
/*!40000 ALTER TABLE `notificaciones` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `promociones`
--

DROP TABLE IF EXISTS `promociones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `promociones` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `descripcion` text DEFAULT NULL,
  `codigo` varchar(50) NOT NULL,
  `fecha_inicio` date NOT NULL,
  `fecha_fin` date NOT NULL,
  `activa` tinyint(1) DEFAULT NULL,
  `uso_maximo` int(11) DEFAULT NULL,
  `usos_actuales` int(11) DEFAULT NULL,
  `servicio_id` int(11) DEFAULT NULL,
  `imagen` varchar(200) DEFAULT NULL,
  `tipo` varchar(20) DEFAULT 'porcentaje',
  `valor` decimal(10,2) DEFAULT 0.00,
  `fecha_creacion` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo` (`codigo`),
  KEY `servicio_id` (`servicio_id`),
  CONSTRAINT `promociones_ibfk_1` FOREIGN KEY (`servicio_id`) REFERENCES `servicios` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `promociones`
--

LOCK TABLES `promociones` WRITE;
/*!40000 ALTER TABLE `promociones` DISABLE KEYS */;
INSERT INTO `promociones` VALUES
(1,'Café con Descuento','Disfruta del mejor café de Boquete con un 15% de descuento en nuestro tour gourmet. Incluye degustación y visita a la finca.','PROMO-4COJET','2026-07-08','2026-10-06',1,50,0,3,'https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=400','porcentaje',15.00,'2026-07-09 01:55:25'),
(2,'Verano en el Archipiélago','Descuento fijo de B/.15 en nuestro tour a Isla San Cristóbal. Snorkel, playas vírgenes y almuerzo incluido.','PROMO-20FA8G','2026-07-08','2026-09-06',1,30,0,10,'https://images.unsplash.com/photo-1540202404-a2f29016b523?w=400','porcentaje',15.00,'2026-07-09 01:55:25');
/*!40000 ALTER TABLE `promociones` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `proveedores`
--

DROP TABLE IF EXISTS `proveedores`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `proveedores` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `tipo` varchar(50) DEFAULT NULL,
  `provincia` varchar(100) DEFAULT NULL,
  `contacto` varchar(100) DEFAULT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `activo` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `direccion` varchar(200) DEFAULT NULL,
  `especificaciones` text DEFAULT NULL,
  `fecha_creacion` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `proveedores`
--

LOCK TABLES `proveedores` WRITE;
/*!40000 ALTER TABLE `proveedores` DISABLE KEYS */;
INSERT INTO `proveedores` VALUES
(1,'Mar y Sol Chiriqui','operador','ChiriquÃ­','Maria Castillo','6000-1001','info@marysolchiriqui.com',1,NULL,'Calle 3ra, David, ChiriquÃ­','{\"actividades\": [\"snorkel\", \"kayak\", \"observacion_aves\", \"fotografia\", \"gastronomico\"], \"capacidad_grupo\": 20, \"duracion_tipica\": \"8_horas\", \"dificultad\": \"facil\", \"equipo\": [\"chalecos\", \"bastones\"], \"incluye_seguro\": true}','2026-07-06 22:36:14'),
(2,'Boquete Mountain Guides','guia','ChiriquÃ­','Roberto Quintero','6000-1002','roberto@boquetonature.com',1,NULL,'Calle El Centro, Boquete, ChiriquÃ­','{\"idiomas\": [\"espanol\", \"ingles\"], \"certificaciones\": [\"guia_naturaleza\", \"guia_aventura\", \"primeros_auxilios\"], \"especialidad\": \"naturaleza\", \"experiencia_anios\": 8}','2026-07-06 22:36:14'),
(3,'Fincas Boquetenias','restaurante','ChiriquÃ­','Ana Lucia Mora','6000-1003','reservas@fincasboquetenas.com',1,NULL,'Finca La Milagrosa, Boquete, ChiriquÃ­','{\"tipo_cocina\": \"tipica\", \"capacidad_comensales\": 20, \"horario_apertura\": \"07:00\", \"horario_cierre\": \"17:00\", \"servicios\": [\"desayuno\", \"almuerzo\"], \"dietas\": [\"vegetariano\", \"vegano\", \"sin_gluten\"]}','2026-07-08 20:31:08'),
(4,'Bocas Travel','operador','Bocas del Toro','Samuel Walker','6000-1004','sam@bocastravel.com',1,NULL,'Calle 4ta, Isla ColÃ³n, Bocas del Toro','{actividades: [snorkel, kayak, cultural, fotografia], capacidad_grupo: 20, duracion_tipica: 3_dias, dificultad: facil, incluye_seguro: true}','2026-07-08 20:31:08'),
(5,'Panama Cultural Tours','operador','PanamÃ¡','Diana Lopez','6000-1005','info@panamacultural.com',1,NULL,'Casco Antiguo, Calle 2da, PanamÃ¡','{\"actividades\": [\"cultural\", \"fotografia\", \"gastronomico\"], \"capacidad_grupo\": 30, \"duracion_tipica\": \"4_horas\", \"dificultad\": \"facil\", \"incluye_seguro\": true}','2026-07-08 20:31:08'),
(6,'Aventura Anton','operador','CoclÃ©','Fernando Rios','6000-1006','fer@aventuraanton.com',1,NULL,'El Valle de AntÃ³n, CoclÃ©','{\"actividades\": [\"senderismo\", \"canopy\", \"ciclismo\", \"escalada\", \"cabalgata\"], \"capacidad_grupo\": 10, \"duracion_tipica\": \"8_horas\", \"dificultad\": \"moderado\", \"equipo\": [\"cascos\", \"arneses\", \"bastones\", \"cuerdas\"], \"incluye_seguro\": true}','2026-07-08 20:31:08');
/*!40000 ALTER TABLE `proveedores` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `recomendaciones_viaje`
--

DROP TABLE IF EXISTS `recomendaciones_viaje`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `recomendaciones_viaje` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `viaje_planificado_id` int(11) NOT NULL,
  `servicio_id` int(11) NOT NULL,
  `score` int(11) DEFAULT 0,
  `creado_en` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `viaje_planificado_id` (`viaje_planificado_id`),
  KEY `servicio_id` (`servicio_id`),
  CONSTRAINT `recomendaciones_viaje_ibfk_1` FOREIGN KEY (`viaje_planificado_id`) REFERENCES `viajes_planificados` (`id`),
  CONSTRAINT `recomendaciones_viaje_ibfk_2` FOREIGN KEY (`servicio_id`) REFERENCES `servicios` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=58 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recomendaciones_viaje`
--

LOCK TABLES `recomendaciones_viaje` WRITE;
/*!40000 ALTER TABLE `recomendaciones_viaje` DISABLE KEYS */;
INSERT INTO `recomendaciones_viaje` VALUES
(1,1,2,45,'2026-07-08 01:32:52'),
(2,1,3,45,'2026-07-08 01:32:52'),
(3,1,5,45,'2026-07-08 01:32:52'),
(4,1,6,45,'2026-07-08 01:32:52'),
(5,1,7,45,'2026-07-08 01:32:52'),
(6,1,1,35,'2026-07-08 01:32:52'),
(7,2,9,80,'2026-07-08 04:07:29'),
(8,2,5,70,'2026-07-08 04:07:29'),
(9,2,10,65,'2026-07-08 04:07:29'),
(10,2,11,65,'2026-07-08 04:07:29'),
(11,2,13,65,'2026-07-08 04:07:29'),
(12,2,7,55,'2026-07-08 04:07:29'),
(13,2,2,45,'2026-07-08 04:07:29'),
(14,2,3,45,'2026-07-08 04:07:29'),
(15,2,6,25,'2026-07-08 04:07:29'),
(16,3,9,80,'2026-07-08 04:07:29'),
(17,3,5,70,'2026-07-08 04:07:29'),
(18,3,10,65,'2026-07-08 04:07:29'),
(19,3,11,65,'2026-07-08 04:07:29'),
(20,3,13,65,'2026-07-08 04:07:29'),
(21,3,7,55,'2026-07-08 04:07:29'),
(22,3,2,45,'2026-07-08 04:07:29'),
(23,3,3,45,'2026-07-08 04:07:29'),
(24,3,6,25,'2026-07-08 04:07:29'),
(25,4,9,80,'2026-07-09 02:09:59'),
(26,4,5,70,'2026-07-09 02:09:59'),
(27,4,11,65,'2026-07-09 02:09:59'),
(28,4,13,65,'2026-07-09 02:09:59'),
(29,4,14,65,'2026-07-09 02:09:59'),
(30,4,7,55,'2026-07-09 02:09:59'),
(31,4,2,45,'2026-07-09 02:09:59'),
(32,4,6,25,'2026-07-09 02:09:59'),
(33,5,9,80,'2026-07-09 02:13:19'),
(34,5,5,70,'2026-07-09 02:13:19'),
(35,5,11,65,'2026-07-09 02:13:19'),
(36,5,13,65,'2026-07-09 02:13:19'),
(37,5,14,65,'2026-07-09 02:13:19'),
(38,5,7,55,'2026-07-09 02:13:19'),
(39,5,2,45,'2026-07-09 02:13:19'),
(40,5,6,25,'2026-07-09 02:13:19'),
(41,6,2,70,'2026-07-09 02:13:47'),
(42,6,11,65,'2026-07-09 02:13:47'),
(43,6,13,65,'2026-07-09 02:13:47'),
(44,6,14,65,'2026-07-09 02:13:47'),
(45,6,7,55,'2026-07-09 02:13:47'),
(46,6,9,55,'2026-07-09 02:13:47'),
(47,6,5,45,'2026-07-09 02:13:47'),
(48,6,6,25,'2026-07-09 02:13:47'),
(49,7,5,75,'2026-07-09 02:14:17'),
(50,7,11,65,'2026-07-09 02:14:17'),
(51,7,13,65,'2026-07-09 02:14:17'),
(52,7,14,65,'2026-07-09 02:14:17'),
(53,7,1,60,'2026-07-09 02:14:17'),
(54,7,9,55,'2026-07-09 02:14:17'),
(55,7,7,25,'2026-07-09 02:14:17'),
(56,8,13,100,'2026-07-09 02:15:56'),
(57,8,7,90,'2026-07-09 02:15:56');
/*!40000 ALTER TABLE `recomendaciones_viaje` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `resenas`
--

DROP TABLE IF EXISTS `resenas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `resenas` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `servicio_id` int(11) NOT NULL,
  `cliente_id` int(11) NOT NULL,
  `reserva_id` int(11) DEFAULT NULL,
  `calificacion` int(11) NOT NULL,
  `comentario` text DEFAULT NULL,
  `fecha_creacion` datetime DEFAULT NULL,
  `activa` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `servicio_id` (`servicio_id`),
  KEY `cliente_id` (`cliente_id`),
  KEY `reserva_id` (`reserva_id`),
  CONSTRAINT `resenas_ibfk_1` FOREIGN KEY (`servicio_id`) REFERENCES `servicios` (`id`),
  CONSTRAINT `resenas_ibfk_2` FOREIGN KEY (`cliente_id`) REFERENCES `clientes` (`id`),
  CONSTRAINT `resenas_ibfk_3` FOREIGN KEY (`reserva_id`) REFERENCES `reservas` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `resenas`
--

LOCK TABLES `resenas` WRITE;
/*!40000 ALTER TABLE `resenas` DISABLE KEYS */;
/*!40000 ALTER TABLE `resenas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `reservas`
--

DROP TABLE IF EXISTS `reservas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `reservas` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tipo` varchar(20) DEFAULT 'reserva',
  `cliente_id` int(11) NOT NULL,
  `servicio_id` int(11) DEFAULT NULL,
  `fecha_reserva` datetime DEFAULT NULL,
  `fecha_gira` datetime DEFAULT NULL,
  `fecha_fin` datetime DEFAULT NULL,
  `fecha_solicitada` datetime DEFAULT NULL,
  `numero_personas` int(11) DEFAULT 1,
  `estado` varchar(20) DEFAULT NULL,
  `total_pago` float DEFAULT 0,
  `presupuesto_estimado` float DEFAULT NULL,
  `presupuesto_tipo` varchar(20) DEFAULT NULL,
  `destino_preferido` varchar(200) DEFAULT NULL,
  `lugar_recogida` varchar(200) DEFAULT NULL,
  `lugares_visitar` text DEFAULT NULL,
  `tipo_alojamiento` varchar(50) DEFAULT NULL,
  `categoria_alojamiento` varchar(50) DEFAULT NULL,
  `transporte` varchar(100) DEFAULT NULL,
  `hospedaje` tinyint(1) DEFAULT 0,
  `alimentacion` varchar(50) DEFAULT NULL,
  `guia` tinyint(1) DEFAULT 0,
  `contacto_preferido` varchar(20) DEFAULT NULL,
  `provincia_cliente` varchar(100) DEFAULT NULL,
  `archivo_adjunto` varchar(200) DEFAULT NULL,
  `observaciones` text DEFAULT NULL,
  `promocion_id` int(11) DEFAULT NULL,
  `descuento_aplicado` float DEFAULT 0,
  `metodo_pago` varchar(20) DEFAULT NULL,
  `tipo_tarjeta` varchar(20) DEFAULT NULL,
  `titular_tarjeta` varchar(200) DEFAULT NULL,
  `ultimos_digitos` varchar(4) DEFAULT NULL,
  `codigo_transaccion` varchar(30) DEFAULT NULL,
  `subtotal` float DEFAULT 0,
  `itbms` float DEFAULT 0,
  `comprobante_pago` varchar(200) DEFAULT NULL,
  `datos_transaccion` text DEFAULT NULL,
  `cotizacion` float DEFAULT NULL,
  `motivo_rechazo` text DEFAULT NULL,
  `fecha_creacion` datetime DEFAULT current_timestamp(),
  `leido` tinyint(1) DEFAULT 0,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_codigo_transaccion` (`codigo_transaccion`),
  KEY `cliente_id` (`cliente_id`),
  KEY `servicio_id` (`servicio_id`),
  KEY `promocion_id` (`promocion_id`),
  CONSTRAINT `reservas_ibfk_1` FOREIGN KEY (`cliente_id`) REFERENCES `clientes` (`id`),
  CONSTRAINT `reservas_ibfk_2` FOREIGN KEY (`servicio_id`) REFERENCES `servicios` (`id`),
  CONSTRAINT `reservas_ibfk_3` FOREIGN KEY (`promocion_id`) REFERENCES `promociones` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reservas`
--

LOCK TABLES `reservas` WRITE;
/*!40000 ALTER TABLE `reservas` DISABLE KEYS */;
INSERT INTO `reservas` VALUES
(5,'reserva',1,6,NULL,'2026-07-24 00:00:00','2026-07-26 00:00:00',NULL,1,'confirmada',374.5,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,NULL,0,NULL,NULL,NULL,NULL,NULL,0,'tarjeta','visa','Stefany Guerrero','5678','TCH-20260707-IZ0M',350,24.5,NULL,NULL,NULL,NULL,'2026-07-08 02:02:05',0),
(6,'reserva',1,4,NULL,'2026-07-19 00:00:00','2026-07-19 00:00:00',NULL,1,'confirmada',96.3,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,NULL,0,NULL,NULL,NULL,NULL,NULL,0,'tarjeta','visa','Stefany Guerrero','3223','TCH-20260707-UOEW',90,6.3,NULL,NULL,NULL,NULL,'2026-07-08 03:16:52',0),
(7,'reserva',2,1,NULL,'2026-07-22 00:00:00','2026-07-22 00:00:00',NULL,1,'confirmada',128.4,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,NULL,0,NULL,NULL,NULL,NULL,NULL,0,'tarjeta','visa','Stefany Guerrero','5467','TCH-20260707-W68K',120,8.4,NULL,NULL,NULL,NULL,'2026-07-08 03:35:21',0),
(8,'reserva',2,7,NULL,'2026-07-16 00:00:00','2026-07-16 00:00:00',NULL,1,'completada',101.65,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,NULL,0,NULL,NULL,NULL,NULL,NULL,0,'tarjeta','visa','Stefany Guerrero','5678','TCH-20260707-AZ5G',95,6.65,NULL,NULL,NULL,NULL,'2026-07-08 03:43:31',0),
(9,'reserva',2,12,NULL,'2026-07-18 00:00:00','2026-07-19 00:00:00',NULL,1,'confirmada',192.6,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,NULL,0,NULL,NULL,NULL,NULL,NULL,0,'tarjeta','visa','Stefany Guerrero','3234','TCH-20260707-0VI1',180,12.6,NULL,NULL,NULL,NULL,'2026-07-08 03:51:09',0),
(10,'reserva',2,7,NULL,'2026-07-17 00:00:00','2026-07-17 00:00:00',NULL,1,'confirmada',101.65,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,NULL,0,NULL,NULL,NULL,NULL,NULL,0,'tarjeta','visa','Stefany Guerrero','3234','TCH-20260707-VZUQ',95,6.65,NULL,NULL,NULL,NULL,'2026-07-08 03:54:49',0),
(11,'reserva',1,9,NULL,'2026-07-17 00:00:00','2026-07-17 00:00:00',NULL,1,'confirmada',69.55,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,NULL,0,NULL,NULL,NULL,NULL,NULL,0,'tarjeta','visa','Stefany Guerrero','5678','TCH-20260707-F4C4',65,4.55,NULL,NULL,NULL,NULL,'2026-07-08 04:13:43',0),
(12,'reserva',2,3,NULL,'2026-07-17 00:00:00','2026-07-17 00:00:00',NULL,4,'confirmada',236.47,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,NULL,0,NULL,NULL,NULL,NULL,NULL,0,'tarjeta','visa','Stefany Guerrero','3234','TCH-20260708-W413',221,15.47,NULL,NULL,NULL,NULL,'2026-07-09 02:00:07',0),
(13,'reserva',2,12,NULL,'2026-07-11 00:00:00','2026-07-12 00:00:00',NULL,1,'confirmada',192.6,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,NULL,0,NULL,NULL,NULL,NULL,NULL,0,'yappy',NULL,NULL,NULL,'TCH-20260708-QUZL',180,12.6,'comprobante_13_TCH-20260708-QUZL.png','{\"id_reserva\": 13, \"codigo_transaccion\": \"TCH-20260708-QUZL\", \"monto\": 192.6, \"moneda\": \"USD\", \"metodo_pago\": \"Yappy\", \"telefono_contacto\": \"7890-7890\", \"fecha_pago\": \"2026-07-08 22:06:12\", \"nombre_cliente\": \"Administrador\", \"email_cliente\": \"admin@turismo.com\", \"tour\": \"Aventura en el Valle de Antón\", \"fecha_gira\": \"2026-07-11\", \"numero_personas\": 1, \"comprobante\": \"comprobante_13_TCH-20260708-QUZL.png\"}',NULL,NULL,'2026-07-09 03:06:12',0),
(14,'solicitud',2,NULL,NULL,'2026-07-15 00:00:00','2026-07-18 00:00:00',NULL,2,'aprobada',0,500,'total','Boquete y Volcan Baru','aeropuerto_david','Cafeteras en Boquete, Volcan Baru, Los Cangilones','cabana','3_estrellas','vehiculo_propio',1,'desayuno',1,'correo',NULL,NULL,'Aqui esta la opcion que vas va con su servicio',NULL,0,NULL,NULL,NULL,NULL,NULL,0,0,NULL,NULL,130,NULL,'2026-07-10 00:53:22',1),
(15,'solicitud',1,NULL,NULL,'2026-07-18 00:00:00','2026-07-20 00:00:00',NULL,5,'aprobada',0,500,'total','Boquete','hotel','Playa de las Lajas','camping','economico','alquiler_auto',1,'todo_incluido',1,'correo',NULL,NULL,'sdsgfgdfgd',NULL,0,NULL,NULL,NULL,NULL,NULL,0,0,NULL,NULL,65,NULL,'2026-07-10 01:16:41',1);
/*!40000 ALTER TABLE `reservas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `servicios`
--

DROP TABLE IF EXISTS `servicios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `servicios` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `descripcion` text DEFAULT NULL,
  `itinerario` text DEFAULT NULL,
  `precio` float NOT NULL,
  `cupo_maximo` int(11) DEFAULT NULL,
  `categoria` varchar(50) DEFAULT NULL,
  `imagen` varchar(200) DEFAULT NULL,
  `activo` tinyint(1) DEFAULT NULL,
  `fecha_creacion` datetime DEFAULT NULL,
  `codigo` varchar(20) DEFAULT NULL,
  `provincia` varchar(100) DEFAULT NULL,
  `distrito` varchar(100) DEFAULT NULL,
  `destino` varchar(100) DEFAULT NULL,
  `punto_salida` varchar(100) DEFAULT NULL,
  `punto_llegada` varchar(100) DEFAULT NULL,
  `duracion_cantidad` int(11) DEFAULT 1,
  `duracion_unidad` varchar(10) DEFAULT 'horas',
  `hora_inicio` varchar(10) DEFAULT NULL,
  `hora_estimada_regreso` varchar(10) DEFAULT NULL,
  `cupos_disponibles` int(11) DEFAULT 0,
  `proveedor_id` int(11) DEFAULT NULL,
  `incluye` text DEFAULT NULL,
  `no_incluye` text DEFAULT NULL,
  `recomendaciones` text DEFAULT NULL,
  `incluye_transporte` tinyint(1) DEFAULT 0,
  `incluye_alimentacion` tinyint(1) DEFAULT 0,
  `incluye_hospedaje` tinyint(1) DEFAULT 0,
  `incluye_guia` tinyint(1) DEFAULT 0,
  `incluye_seguro` tinyint(1) DEFAULT 0,
  `incluye_entradas` tinyint(1) DEFAULT 0,
  `incluye_equipo` tinyint(1) DEFAULT 0,
  `transporte` varchar(100) DEFAULT NULL,
  `transporte_precios` text DEFAULT NULL,
  `tipo_experiencia` varchar(100) DEFAULT NULL,
  `duracion_recomendada` varchar(50) DEFAULT NULL,
  `tipo` varchar(20) DEFAULT 'programado',
  `tipo_programacion` varchar(20) DEFAULT 'recurrente',
  `dias_operacion` varchar(50) DEFAULT NULL,
  `fecha_unica` date DEFAULT NULL,
  `vigencia_inicio` date DEFAULT NULL,
  `vigencia_fin` date DEFAULT NULL,
  `hora_salida_tour` varchar(10) DEFAULT NULL,
  `hora_regreso_tour` varchar(10) DEFAULT NULL,
  `dias_minimos` int(11) DEFAULT 1,
  `dias_maximos` int(11) DEFAULT 7,
  `requiere_hospedaje` tinyint(1) DEFAULT 0,
  `requiere_alimentacion` tinyint(1) DEFAULT 0,
  `requiere_guia` tinyint(1) DEFAULT 1,
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo` (`codigo`),
  KEY `proveedor_id` (`proveedor_id`),
  CONSTRAINT `servicios_ibfk_1` FOREIGN KEY (`proveedor_id`) REFERENCES `proveedores` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `servicios`
--

LOCK TABLES `servicios` WRITE;
/*!40000 ALTER TABLE `servicios` DISABLE KEYS */;
INSERT INTO `servicios` VALUES
(1,'Golfo de Chiriquí','Explora las paradisíacas islas del Golfo de Chiriquí. Un recorrido en lancha que te llevará a descubrir playas vírgenes, avistamiento de delfines y una experiencia única en el Pacífico panameño.','08:00 AM - Salida desde David (punto de encuentro)\r\n08:30 AM - Traslado al puerto\r\n09:00 AM - Inicio del recorrido en lancha\r\n09:30 AM - Avistamiento de delfines\r\n10:30 AM - Llegada a Isla Palenque\r\n10:45 AM - Tiempo libre en la playa\r\n11:30 AM - Almuerzo tipo picnic\r\n12:30 PM - Regreso al puerto\r\n01:00 PM - Llegada a David y fin del tour',120,20,'islas','https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&h=400&fit=crop',1,'2026-07-04 16:35:20','TOUR-32Z06J','Chiriquí','David','Golfo de Chiriquí','David','Isla Palenque',4,'horas','08:00','12:00',20,1,'Transporte en lancha desde David\r\nGuía turístico especializado\r\nSeguro de viaje\r\nAlmuerzo tipo picnic en la isla\r\nSnorkel y equipo de playa\r\nAvistamiento de delfines','Bebidas alcohólicas\r\nGastos personales\r\nPropinas\r\nTransporte desde otras provincias','- Llevar bloqueador solar\r\n- Ropa de baño\r\n- Toalla\r\n- Gafas de sol\r\n- Cámara fotográfica\r\n- Repelente de insectos\r\n- Zapatos cómodos\r\n- Agua potable\r\n- Snacks\r\n- Sombrero o gorra\r\n- Efectivo para compras adicionales',1,1,0,1,1,1,0,'lancha','{\"lancha\": 15.0}','islas','1_dia','programado','recurrente','2,5,6',NULL,'2026-07-04','2027-12-15','06:00','14:00',1,7,0,0,1),
(2,'Snorkel en Isla Coiba','Explora las aguas cristalinas del Parque Nacional Coiba. Buceo ligero y snorkel en arrecifes vírgenes con guía especializado. Ideal para amantes de la vida marina.','05:30 AM - Recojo en hoteles de David\n06:00 AM - Salida a Puerto Mutis\n07:30 AM - Llegada a Isla Coiba\n08:00 AM - Snorkel en arrecifes\n10:00 AM - Refrigerio en la playa\n11:00 AM - Snorkel segunda parada\n12:30 PM - Almuerzo en la isla\n02:00 PM - Regreso a Puerto Mutis\n04:00 PM - Llegada a David',85,20,'playa','https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=400',1,NULL,'TOUR-SNORKEL','Chiriquí','Barú','Golfo de Chiriquí','Hotel en David',NULL,1,'dias','06:00','16:00',20,1,'Snorkel\n Guía\n Transporte\n Almuerzo\n Equipo','Fotos subacuáticas\n Bebidas alcohólicas','Llevar bloqueador resistente al agua\n toalla\n muda de ropa',1,0,0,1,0,0,0,'lancha','{\"lancha\": 25}','playa',NULL,'programado','recurrente','0,1,3,4,5,6',NULL,NULL,NULL,'06:00','16:00',1,7,0,0,1),
(3,'Tour del Café en Boquete','Recorrido por fincas cafetaleras de Boquete. Cata de café de especialidad, proceso de tueste y siembra. Incluye visita a Finca Lérida.','07:00 AM - Recojo en hoteles de Boquete\n07:30 AM - Desayuno típico\n08:30 AM - Recorrido por plantación de café\n10:00 AM - Proceso de lavado y secado\n11:30 AM - Cata de café especial\n12:30 PM - Almuerzo en finca\n02:00 PM - Tour por el jardín botánico\n03:30 PM - Regreso al hotel',65,15,'gastronomica','https://images.unsplash.com/photo-1498804103079-a6351b050096?w=400',1,NULL,'TOUR-CAFE','Chiriquí','Boquete','Boquete','Centro de Boquete',NULL,1,'dias','07:30','13:00',15,3,'Cata de café\n Desayuno típico\n Transporte\n Guía','Compras adicionales\n Transporte nocturno','Llevar zapatos cómodos\n sombrero\n cámara',1,0,0,1,0,0,0,'vehiculo_propio','{\"vehiculo_propio\": 0}','gastronomica',NULL,'programado','recurrente','0,1,2,3,4,5',NULL,NULL,NULL,'07:30','13:00',1,7,0,0,1),
(4,'Ascenso al Volcán Barú','Caminata guiada al punto más alto de Panamá. Salida nocturna para ver el amanecer desde la cima. Vista espectacular del Caribe y el Pacífico.','03:00 AM - Salida desde David\n04:30 AM - Inicio de ascenso desde el campamento\n06:30 AM - Llegada a la cima (amanecer)\n07:00 AM - Desayuno con vista al Pacífico y Caribe\n08:00 AM - Descenso\n10:00 AM - Regreso a David',90,10,'montana','https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=400',1,NULL,'TOUR-VOLCAN','Chiriquí','Boquete','Volcán Barú','Boquete',NULL,1,'dias','23:00','12:00',10,2,'Guía certificado\n Bastones de trekking\n Snacks\n Seguro','Equipo de camping\n Ropa de abrigo','Llevar ropa térmica\n linterna frontal\n agua 2L\n repelente',0,0,0,1,0,0,0,'vehiculo_propio','{\"vehiculo_propio\": 0}','montana',NULL,'programado','recurrente','0,6',NULL,NULL,NULL,'23:00','12:00',1,7,0,0,1),
(5,'Paseo en kayak por manglares','Navegación en kayak por manglares del Pacífico chiricano. Observación de aves exóticas, monos y vida silvestre. Guía naturalista bilingüe.','08:00 AM - Punto de encuentro en el malecón\n08:30 AM - Instrucciones y equipo de seguridad\n09:00 AM - Inicio del recorrido en kayak\n10:30 AM - Parada en islote para fotos\n11:00 AM - Exploración de canales\n12:30 PM - Almuerzo en restaurante local\n02:00 PM - Kayak por el manglar\n03:30 PM - Regreso al punto de inicio',45,12,'ecoturismo','https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=400',1,NULL,'TOUR-MANGROVE','Chiriquí','David','Golfo de Chiriquí','Muelle de Boca Chica',NULL,4,'horas','08:00','12:00',12,1,'Kayak\n Chaleco salvavidas\n Guía\n Agua\n Snack','Transporte al punto de encuentro\n Fotos','Llevar ropa ligera\n sandalias\n bloqueador\n repelente',0,0,0,1,0,0,0,'vehiculo_propio','{\"vehiculo_propio\": 0}','ecoturismo',NULL,'programado','recurrente','1,2,3,4,5',NULL,NULL,NULL,'08:00','12:00',1,7,0,0,1),
(6,'Bocas del Toro - 3 días','Paquete completo de 3 días en el archipiélago de Bocas del Toro. Snorkel en Isla Bastimentos, paseo en bote por los canales, playas escondidas y vida nocturna.','Día 1:\r\n07:00 AM - Salida desde David\r\n10:00 AM - Ferry a Bocas del Toro\r\n12:00 PM - Llegada e instalación en hotel\r\n02:00 PM - Snorkel en Playa Estrella\r\n07:00 PM - Cena en el pueblo\r\n\r\nDía 2:\r\n08:00 AM - Desayuno\r\n09:00 AM - Tour en lancha por islas\r\n12:00 PM - Almuerzo en playa\r\n02:00 PM - Tiempo libre\r\n\r\nDía 3:\r\n08:00 AM - Desayuno\r\n09:00 AM - Regreso a David',350,20,'playa','https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTw3kSn4E69JD3WTCYCmdvj14QeyIKGoO0CWyvtpdiYCQ&s=10',1,NULL,'TOUR-BOCAS','Bocas del Toro','Bocas del Toro','Isla Colón','Terminal de David','',3,'dias','07:00','09:00',20,4,'Hospedaje 2 noches\r\n Snorkel\r\n Guía\r\n Transporte marítimo\r\n Desayunos','Vuelos\r\n Alimentación no incluida\r\n Seguro de viaje','Llevar traje de baño\r\n repelente\r\n linterna\r\n efectivo',1,0,0,1,0,0,0,'lancha','{\"lancha\": 25}','playa','','programado','recurrente','3,4,5,6',NULL,NULL,NULL,'08:00','17:00',1,7,0,0,1),
(7,'City Tour Panamá','Recorrido por el Casco Antiguo, Cinta Costera, Panamá Viejo y Esclusas de Miraflores. Guía experto en historia panameña. Incluye almuerzo típico.','06:00 AM - Salida desde David\r\n09:00 AM - Llegada a Ciudad de Panamá\r\n10:00 AM - Casco Antiguo (tour peatonal)\r\n12:00 PM - Almuerzo en restaurante típico\r\n01:30 PM - Cinta Costera y Amador\r\n03:00 PM - Esclusas de Miraflores\r\n05:00 PM - Regreso a David',95,30,'cultural','https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTQhg8LeIZF80wQegFNvXxNnUK4CRi_2prECPFTHhSYWg&s=10',1,NULL,'TOUR-PANAMA','Panamá','Panamá','Ciudad de Panamá','Hotel en Ciudad de Panamá','',1,'dias','06:00','05:00',30,5,'Guía\r\n Almuerzo\r\n Entrada a museos\r\n Transporte\r\n Agua','Compras personales\r\n Propinas','Llevar ropa fresca\r\n sombrero\r\n cámara\r\n zapatos cómodos',1,0,0,1,0,0,0,'transporte_empresa','{\"transporte_empresa\": 15}','cultural','','programado','recurrente','0,1,2,3,4,5',NULL,NULL,NULL,'08:00','17:00',1,7,0,0,1),
(9,'Sendero Los Quetzales - Día Completo','Caminata guiada por el famoso Sendero Los Quetzales. Avistamiento de aves, bosque nuboso y paisajes increíbles.','06:00 - Salida desde Boquete\n07:00 - Inicio de caminata\n09:00 - Descanso y café\n12:00 - Almuerzo en la cima\n14:00 - Retorno\n16:00 - Llegada a Boquete',65,15,'ecoturismo','https://images.unsplash.com/photo-1506905925346-21bda4d32df4',1,NULL,'TOUR-001','Chiriqui','Boquete','Parque Nacional Volcán Barú','Boquete centro',NULL,1,'dias','06:00','16:00',15,2,'Guía bilingüe certificado\nSnacks y agua\nSeguro de accidentes\nEntrada al parque','Transporte al punto de encuentro\nAlmuerzo','Llevar ropa impermeable\nZapatos de senderismo\nRepelente de insectos',0,0,0,1,1,1,0,'vehiculo_propio,autobus,transporte_empresa','{\"vehiculo_propio\": 0, \"autobus\": 10, \"transporte_empresa\": 25}','ecoturismo','1_dia','programado','recurrente','0,1,2,3,4,5,6',NULL,NULL,NULL,NULL,NULL,1,7,0,0,1),
(10,'Isla San Cristóbal - Snorkel y Playas','Excursión en lancha a Isla San Cristóbal. Snorkel en arrecifes, playas vírgenes y almuerzo típico.','08:00 - Salida del muelle\n09:00 - Snorkel en Coral Gardens\n11:00 - Isla San Cristóbal\n12:00 - Almuerzo\n14:00 - Playa y descanso\n16:00 - Retorno',85,12,'islas','https://images.unsplash.com/photo-1540202404-a2f29016b523',1,NULL,'TOUR-002','Bocas del Toro','Isla Colón','Isla San Cristóbal','Muelle de Bocas',NULL,1,'dias','08:00','17:00',12,4,'Lancha ida y vuelta\nEquipo de snorkel\nAlmuerzo típico\nGuía','Bebidas alcohólicas\nToallas','Protector solar biodegradable\nRopa de baño\nCámara subacuática',1,1,0,1,1,1,1,'lancha,transporte_empresa','{\"lancha\": 18, \"transporte_empresa\": 15}','islas','1_dia','programado','recurrente','2,3,4,5,6',NULL,NULL,NULL,NULL,NULL,1,7,0,0,1),
(11,'Ruta del Café - Finca Gourmet','Recorrido por plantación de café de altura. Degustación, proceso de tostado y maridaje con chocolate artesanal.','09:00 - Recepción en finca\n09:30 - Recorrido por plantación\n10:30 - Proceso de tostado\n11:30 - Degustación\n12:30 - Maridaje con chocolate',45,20,'gastronomica','https://images.unsplash.com/photo-1495474472287-4d71bcdd2085',1,NULL,'TOUR-003','Chiriqui','Boquete','Finca Café de Altura','Boquete centro',NULL,1,'dias','09:00','13:00',20,3,'Guía especializado\nDegustación de 5 cafés\nChocolate artesanal\nCertificado','Transporte','Llegar con ropa cómoda\nNo usar perfume (afecta la degustación)',0,1,0,1,0,1,0,'vehiculo_propio,transporte_empresa','{\"vehiculo_propio\": 0, \"transporte_empresa\": 12}','gastronomica','medio_dia','programado','recurrente','1,2,3,4,5',NULL,NULL,NULL,NULL,NULL,1,7,0,0,1),
(12,'Aventura en el Valle de Antón','Canopy, rappel y senderismo en el cráter de un volcán extinto. Ideal para adrenalina.','Día 1:\n07:00 - Salida de Panamá\n09:00 - Canopy\n12:00 - Almuerzo\n14:00 - Senderismo La India Dormida\nDía 2:\n08:00 - Rappel cascada\n12:00 - Almuerzo\n15:00 - Retorno',180,10,'aventura','https://images.unsplash.com/photo-1551632811-561732d1e306',1,NULL,'TOUR-004','Cocle','Antón','El Valle de Antón','Panamá - Albrook',NULL,2,'dias','07:00','17:00',10,6,'Transporte desde Panamá\nEquipo de canopy y rappel\nGuía certificado\n2 almuerzos\nSeguro','Hospedaje\nCenas','Ropa deportiva\nZapatos cerrados\nMuda de ropa extra',1,1,0,1,1,1,1,'autobus,transporte_empresa','{\"autobus\": 12, \"transporte_empresa\": 30}','aventura','2_3_dias','programado','recurrente','5,6',NULL,NULL,NULL,NULL,NULL,1,7,0,0,1),
(13,'Historia en Casco Viejo','Recorrido a pie por el Casco Antiguo de Panamá. Museos, arquitectura colonial y gastronomía local.','09:00 - Plaza Independencia\n10:00 - Museo del Canal\n12:00 - Almuerzo en típico\n14:00 - Iglesia San José\n15:00 - Palacio de las Garzas\n16:00 - Mercado artesanal',55,25,'historico','https://images.unsplash.com/photo-1587583770025-32851e0f38f4',1,NULL,'TOUR-005','Panama','San Felipe','Casco Viejo','Plaza de la Independencia',NULL,1,'dias','09:00','17:00',25,5,'Guía histórico\nEntradas a museos\nAlmuerzo\nAgua','Transporte al punto de encuentro\nCompras personales','Zapatos cómodos\nRopa fresca\nProtector solar',0,1,0,1,0,1,0,'vehiculo_propio,transporte_empresa','{\"vehiculo_propio\": 0, \"transporte_empresa\": 10}','historico','1_dia','programado','recurrente','1,2,3,4,5,6',NULL,NULL,NULL,NULL,NULL,1,7,0,0,1),
(14,'Montaña y Neblina - Cerro Punta','Escapada a las tierras altas de Chiriquí. Visita a huertas orgánicas, fresa con crema y paisajes de montaña.','05:00 - Salida de David\n07:00 - Desayuno típico\n08:00 - Recorrido huertas\n10:00 - Fresa con crema\n11:00 - Mirador La Nevera\n12:00 - Almuerzo\n14:00 - Pueblo de Cerro Punta\n16:00 - Retorno',50,18,'montana','https://images.unsplash.com/photo-1585409677983-0f6c41ca9c3b',1,NULL,'TOUR-006','Chiriqui','Cerro Punta','Cerro Punta','David centro',NULL,1,'dias','05:00','18:00',18,2,'Guía\nDesayuno y almuerzo\nEntrada a huertas','Transporte\nFresa con crema ($3)','Ropa abrigada (8-15°C)\nImpermeable\nCámara fotográfica',0,1,0,1,0,1,0,'vehiculo_propio,autobus,transporte_empresa','{\"vehiculo_propio\": 0, \"autobus\": 8, \"transporte_empresa\": 20}','montana','1_dia','programado','recurrente','0,2,4,6',NULL,NULL,NULL,NULL,NULL,1,7,0,0,1),
(15,'prueba replicacion',NULL,NULL,100,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,'horas',NULL,NULL,0,NULL,NULL,NULL,NULL,0,0,0,0,0,0,0,NULL,NULL,NULL,NULL,'programado','recurrente',NULL,NULL,NULL,NULL,NULL,NULL,1,7,0,0,1),
(16,'prueba replicacion',NULL,NULL,100,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,'horas',NULL,NULL,0,NULL,NULL,NULL,NULL,0,0,0,0,0,0,0,NULL,NULL,NULL,NULL,'programado','recurrente',NULL,NULL,NULL,NULL,NULL,NULL,1,7,0,0,1),
(17,'servicio replica test',NULL,NULL,500,10,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,'horas',NULL,NULL,0,NULL,NULL,NULL,NULL,0,0,0,0,0,0,0,NULL,NULL,NULL,NULL,'programado','recurrente',NULL,NULL,NULL,NULL,NULL,NULL,1,7,0,0,1);
/*!40000 ALTER TABLE `servicios` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `solicitudes`
--

DROP TABLE IF EXISTS `solicitudes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `solicitudes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cliente_id` int(11) NOT NULL,
  `servicio_id` int(11) DEFAULT NULL,
  `fecha_inicio` date NOT NULL,
  `fecha_fin` date DEFAULT NULL,
  `numero_personas` int(11) DEFAULT NULL,
  `presupuesto_estimado` float DEFAULT NULL,
  `presupuesto_tipo` varchar(20) DEFAULT NULL,
  `destino_preferido` varchar(200) DEFAULT NULL,
  `lugar_recogida` varchar(200) DEFAULT NULL,
  `lugares_visitar` text DEFAULT NULL,
  `tipo_alojamiento` varchar(50) DEFAULT NULL,
  `categoria_alojamiento` varchar(50) DEFAULT NULL,
  `transporte` varchar(100) DEFAULT NULL,
  `hospedaje` tinyint(1) DEFAULT NULL,
  `alimentacion` varchar(50) DEFAULT NULL,
  `guia` tinyint(1) DEFAULT NULL,
  `contacto_preferido` varchar(20) DEFAULT NULL,
  `provincia_cliente` varchar(100) DEFAULT NULL,
  `archivo_adjunto` varchar(200) DEFAULT NULL,
  `observaciones` text DEFAULT NULL,
  `estado` varchar(20) DEFAULT NULL,
  `cotizacion` float DEFAULT NULL,
  `fecha_solicitada` datetime DEFAULT NULL,
  `fecha_creacion` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `cliente_id` (`cliente_id`),
  KEY `servicio_id` (`servicio_id`),
  CONSTRAINT `solicitudes_ibfk_1` FOREIGN KEY (`cliente_id`) REFERENCES `clientes` (`id`),
  CONSTRAINT `solicitudes_ibfk_2` FOREIGN KEY (`servicio_id`) REFERENCES `servicios` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `solicitudes`
--

LOCK TABLES `solicitudes` WRITE;
/*!40000 ALTER TABLE `solicitudes` DISABLE KEYS */;
/*!40000 ALTER TABLE `solicitudes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `transacciones`
--

DROP TABLE IF EXISTS `transacciones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `transacciones` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `reserva_id` int(11) NOT NULL,
  `monto` float NOT NULL,
  `metodo_pago` varchar(50) DEFAULT NULL,
  `comprobante_url` varchar(200) DEFAULT NULL,
  `fecha_pago` datetime DEFAULT NULL,
  `estado_pago` varchar(20) DEFAULT NULL,
  `json_generado` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `reserva_id` (`reserva_id`),
  CONSTRAINT `transacciones_ibfk_1` FOREIGN KEY (`reserva_id`) REFERENCES `reservas` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `transacciones`
--

LOCK TABLES `transacciones` WRITE;
/*!40000 ALTER TABLE `transacciones` DISABLE KEYS */;
/*!40000 ALTER TABLE `transacciones` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `nombre_completo` varchar(100) NOT NULL,
  `password_hash` varchar(128) NOT NULL,
  `rol` varchar(20) DEFAULT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `fecha_registro` datetime DEFAULT NULL,
  `activo` tinyint(1) DEFAULT NULL,
  `reset_token` varchar(100) DEFAULT NULL,
  `reset_token_expira` datetime DEFAULT NULL,
  `fecha_creacion` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios`
--

LOCK TABLES `usuarios` WRITE;
/*!40000 ALTER TABLE `usuarios` DISABLE KEYS */;
INSERT INTO `usuarios` VALUES
(1,'admin','admin@turismo.com','Administrador','$2b$12$OktAgKq399og603.nwzsYenq90NPQrjNBQfMchm2ET/G67JePCvLi','admin',NULL,'2026-07-01 03:26:21',1,NULL,NULL,'2026-07-04 21:51:26'),
(2,'stefany_78','stefanyrachel11@gmail.com','Stefany Guerrero','$2b$12$c5.zRV2nHqWuOWUBmfIxNOIamd3Cl4WoG1EgTY.TsNdL6ayPQTXO.','cliente','6330-1291','2026-07-01 03:30:04',1,NULL,NULL,'2026-07-04 21:51:26'),
(3,'sofi_02','arauzstefany85@gmail.com','Sofia Olmos','$2b$12$tbM6k1Wnstj3idJ/B0BoAuzvgLzQb5YEE8NAVxWJp3Ag98L3yvh6W','cliente','6330-1291','2026-07-01 03:42:50',1,NULL,NULL,'2026-07-04 21:51:26');
/*!40000 ALTER TABLE `usuarios` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `viajes_planificados`
--

DROP TABLE IF EXISTS `viajes_planificados`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `viajes_planificados` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cliente_id` int(11) NOT NULL,
  `fecha_inicio` date NOT NULL,
  `fecha_fin` date NOT NULL,
  `numero_personas` int(11) NOT NULL,
  `presupuesto` decimal(10,2) DEFAULT NULL,
  `transporte_preferido` varchar(50) DEFAULT NULL,
  `experiencia_buscada` varchar(50) DEFAULT NULL,
  `requiere_hospedaje` tinyint(1) DEFAULT 0,
  `requiere_alimentacion` tinyint(1) DEFAULT 0,
  `requiere_guia` tinyint(1) DEFAULT 1,
  `destino_preferido` varchar(100) DEFAULT NULL,
  `observaciones` text DEFAULT NULL,
  `estado` varchar(20) DEFAULT 'planificando',
  `fecha_creacion` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `cliente_id` (`cliente_id`),
  CONSTRAINT `viajes_planificados_ibfk_1` FOREIGN KEY (`cliente_id`) REFERENCES `clientes` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `viajes_planificados`
--

LOCK TABLES `viajes_planificados` WRITE;
/*!40000 ALTER TABLE `viajes_planificados` DISABLE KEYS */;
INSERT INTO `viajes_planificados` VALUES
(1,2,'2026-07-10','2026-07-12',2,NULL,'','',0,0,1,NULL,NULL,'recomendado','2026-07-08 01:32:52'),
(2,1,'2026-07-23','2026-07-31',4,500.00,'transporte_empresa','ecoturismo',1,1,1,'Isla Colón','asdfghjhasdfg','recomendado','2026-07-08 04:07:29'),
(3,1,'2026-07-23','2026-07-31',4,500.00,'transporte_empresa','ecoturismo',1,1,1,'Isla Colón','asdfghjhasdfg','recomendado','2026-07-08 04:07:29'),
(4,1,'2026-07-24','2026-07-31',3,500.00,'transporte_empresa','ecoturismo',1,1,1,'Isla San Cristóbal','','recomendado','2026-07-09 02:09:59'),
(5,1,'2026-07-24','2026-07-24',3,500.00,'transporte_empresa','ecoturismo',1,1,1,'Isla San Cristóbal','','recomendado','2026-07-09 02:13:19'),
(6,1,'2026-07-17','2026-07-17',3,NULL,'transporte_empresa','aventura',1,1,1,'','','recomendado','2026-07-09 02:13:47'),
(7,1,'2026-07-08','2026-07-10',3,NULL,'vehiculo_propio','playa',1,1,1,'','','recomendado','2026-07-09 02:14:17'),
(8,1,'2026-07-08','2026-07-10',4,500.00,'transporte_empresa','cultural',0,1,1,'','','recomendado','2026-07-09 02:15:56');
/*!40000 ALTER TABLE `viajes_planificados` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*M!100616 SET NOTE_VERBOSITY=@OLD_NOTE_VERBOSITY */;

-- Dump completed on 2026-07-10 10:14:21
