SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `dbkf2017`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `Consignaciones`
--

CREATE TABLE `Consignaciones` (
  `id_consignacion` bigint(20) NOT NULL,
  `numc_usuario` bigint(20) NOT NULL,
  `monto_consig` int(11) NOT NULL,
  `fecha_consig` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `Retiros`
--

CREATE TABLE `Retiros` (
  `id_retiro` bigint(20) NOT NULL,
  `numc_usuario` bigint(20) NOT NULL,
  `monto_retiro` bigint(20) NOT NULL,
  `fecha_inicio_retiro` datetime NOT NULL,
  `fecha_fin_retiro` datetime NOT NULL DEFAULT '1900-08-01 00:00:00',
  `estado_retiro` char(1) NOT NULL DEFAULT 'E'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `Traslados`
--

CREATE TABLE `Traslados` (
  `id_traslado` bigint(20) NOT NULL,
  `numc_usuario_expedidor` bigint(20) NOT NULL,
  `numc_usuario_receptor` bigint(20) NOT NULL,
  `monto_traslado` bigint(20) NOT NULL,
  `fecha_inicio_traslado` datetime NOT NULL,
  `fecha_fin_traslado` datetime NOT NULL DEFAULT '1900-08-01 00:00:00',
  `estado_traslado` char(1) NOT NULL DEFAULT 'E'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `Usuarios`
--

CREATE TABLE `Usuarios` (
  `num_cuenta` bigint(20) NOT NULL,
  `saldo` bigint(20) NOT NULL DEFAULT '500',
  `nombre` varchar(45) NOT NULL,
  `apellido` varchar(45) NOT NULL,
  `email` varchar(70) NOT NULL,
  `estado` char(1) NOT NULL DEFAULT 'A'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
;


--
-- Indices de la tabla `Consignaciones`
--
ALTER TABLE `Consignaciones`
  ADD PRIMARY KEY (`id_consignacion`),
  ADD KEY `fk_Consignaciones_idx` (`numc_usuario`);

--
-- Indices de la tabla `Retiros`
--
ALTER TABLE `Retiros`
  ADD PRIMARY KEY (`id_retiro`),
  ADD KEY `fk_Retiros_Usuarios_idx` (`numc_usuario`);

--
-- Indices de la tabla `Traslados`
--
ALTER TABLE `Traslados`
  ADD PRIMARY KEY (`id_traslado`),
  ADD KEY `fk_Transacciones_Usuarios_1_idx` (`numc_usuario_expedidor`),
  ADD KEY `fk_Transacciones_Usuarios_2_idx` (`numc_usuario_receptor`);

--
-- Indices de la tabla `Usuarios`
--
ALTER TABLE `Usuarios`
  ADD PRIMARY KEY (`num_cuenta`),
  ADD UNIQUE KEY `email` (`email`);

  
--
-- AUTO_INCREMENT de la tabla `Consignaciones`
--
ALTER TABLE `Consignaciones`
  MODIFY `id_consignacion` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;
--
-- AUTO_INCREMENT de la tabla `Retiros`
--
ALTER TABLE `Retiros`
  MODIFY `id_retiro` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8341;
--
-- AUTO_INCREMENT de la tabla `Traslados`
--
ALTER TABLE `Traslados`
  MODIFY `id_traslado` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2208;


--
-- Filtros para la tabla `Consignaciones`
--
ALTER TABLE `Consignaciones`
  ADD CONSTRAINT `fk_Consignaciones_Usuarios` FOREIGN KEY (`numc_usuario`) REFERENCES `Usuarios` (`num_cuenta`) ON DELETE NO ACTION ON UPDATE NO ACTION;

--
-- Filtros para la tabla `Retiros`
--
ALTER TABLE `Retiros`
  ADD CONSTRAINT `fk_Retiros_Usuarios` FOREIGN KEY (`numc_usuario`) REFERENCES `Usuarios` (`num_cuenta`) ON DELETE NO ACTION ON UPDATE NO ACTION;

--
-- Filtros para la tabla `Traslados`
--
ALTER TABLE `Traslados`
  ADD CONSTRAINT `fk_Transacciones_Usuarios_1` FOREIGN KEY (`numc_usuario_expedidor`) REFERENCES `Usuarios` (`num_cuenta`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  ADD CONSTRAINT `fk_Transacciones_Usuarios_2` FOREIGN KEY (`numc_usuario_receptor`) REFERENCES `Usuarios` (`num_cuenta`) ON DELETE NO ACTION ON UPDATE NO ACTION;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
