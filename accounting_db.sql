-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Nov 21, 2025 at 01:14 PM
-- Server version: 8.0.30
-- PHP Version: 8.1.10

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `accounting_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `accounting_account`
--

CREATE TABLE `accounting_account` (
  `id` bigint NOT NULL,
  `code` varchar(20) NOT NULL,
  `name` varchar(255) NOT NULL,
  `account_type` varchar(20) NOT NULL,
  `is_active` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `accounting_account`
--

INSERT INTO `accounting_account` (`id`, `code`, `name`, `account_type`, `is_active`) VALUES
(1, '104', 'Perlengkapan Outbond', 'asset', 1),
(2, '101', 'Kas', 'asset', 1),
(3, '103', 'Persediaan Merchandise', 'asset', 1),
(4, '102', 'Piutang Usaha', 'asset', 1),
(5, '105', 'Peralatan Outbond', 'asset', 1),
(6, '106', 'Kendaraan Operasional', 'asset', 1),
(7, '107', 'Akumulasi Penyusutan', 'asset', 1),
(8, '108', 'Sewa Dibayar di Muka', 'asset', 1),
(9, '201', 'Hutang Usaha', 'liability', 1),
(10, '202', 'Pendapatan Diterima', 'liability', 1),
(11, '203', 'Hutang Gaji', 'liability', 1),
(12, '204', 'Hutang Pajak', 'liability', 1),
(13, '205', 'Hutang Bank', 'liability', 1),
(14, '301', 'Modal Pemilik', 'equity', 1),
(15, '302', 'Laba Ditahan', 'equity', 1),
(16, '401', 'Prive', 'prive', 1),
(17, '501', 'Pendapatan Outbond', 'revenue', 1),
(18, '502', 'Pendapatan Merchandise', 'revenue', 1),
(19, '503', 'Pendapatan Sewa Fasilitas', 'revenue', 1),
(20, '504', 'Pendapatan Lain-lain', 'revenue', 1),
(21, '601', 'Beban Gaji', 'expense', 1),
(22, '602', 'Beban Perlengkapan', 'expense', 1),
(23, '603', 'Beban Pemeliharaan', 'expense', 1),
(24, '604', 'Beban Konsumsi', 'expense', 1),
(25, '605', 'Beban Sewa', 'expense', 1),
(26, '606', 'Beban Listrik dan Air', 'expense', 1),
(27, '607', 'Beban Promosi', 'expense', 1),
(28, '608', 'Beban Administrasi', 'expense', 1),
(29, '609', 'Beban Penyusutan', 'expense', 1),
(30, '610', 'Beban Lain-lain', 'expense', 1);

-- --------------------------------------------------------

--
-- Table structure for table `accounting_closingstatus`
--

CREATE TABLE `accounting_closingstatus` (
  `id` bigint NOT NULL,
  `year` int NOT NULL,
  `is_closed` tinyint(1) NOT NULL,
  `closed_at` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `accounting_closingstatus`
--

INSERT INTO `accounting_closingstatus` (`id`, `year`, `is_closed`, `closed_at`) VALUES
(1, 2025, 1, '2025-11-18 10:14:19.112114');

-- --------------------------------------------------------

--
-- Table structure for table `accounting_company`
--

CREATE TABLE `accounting_company` (
  `id` bigint NOT NULL,
  `name` varchar(255) NOT NULL,
  `logo` varchar(100) DEFAULT NULL,
  `currency` varchar(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `accounting_company`
--

INSERT INTO `accounting_company` (`id`, `name`, `logo`, `currency`) VALUES
(1, 'D\'Pongs Wisata Keluarga', 'company_logos/logo.png', 'IDR');

-- --------------------------------------------------------

--
-- Table structure for table `accounting_journalentry`
--

CREATE TABLE `accounting_journalentry` (
  `id` bigint NOT NULL,
  `date` date NOT NULL,
  `number` varchar(100) NOT NULL,
  `description` longtext NOT NULL,
  `is_adjustment` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `company_id` bigint DEFAULT NULL,
  `created_by_id` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `accounting_journalentry`
--

INSERT INTO `accounting_journalentry` (`id`, `date`, `number`, `description`, `is_adjustment`, `created_at`, `company_id`, `created_by_id`) VALUES
(13, '2025-01-02', 'L12113', 'Setoran modal pemilik', 0, '2025-11-20 13:44:15.549462', NULL, 1),
(14, '2025-01-03', 'AA12', 'Peralatan outbond', 0, '2025-11-20 13:46:43.365118', NULL, 1),
(15, '2025-01-05', 'E243', 'Pembelian perlengkapan', 0, '2025-11-20 13:48:02.099935', NULL, 1),
(16, '2025-01-08', 'PO32', 'Penjualan paket outbond', 0, '2025-11-20 13:49:00.382324', NULL, 1),
(17, '2025-01-10', 'MK32', 'Penjualan merchandise', 0, '2025-11-20 13:49:51.621857', NULL, 1),
(18, '2025-01-12', 'PM3432', 'Pembelian merchandise', 0, '2025-11-20 13:50:52.191277', NULL, 1),
(19, '2025-01-07', 'PP43', 'Penerimaan piutang', 0, '2025-11-20 13:51:46.513024', NULL, 1),
(20, '2025-01-15', 'PU2343', 'Pembayaran utang usaha', 0, '2025-11-20 13:52:37.713649', NULL, 1),
(21, '2025-01-18', 'PP34', 'Penerimaan pendapatan', 0, '2025-11-20 13:53:31.629718', NULL, 1),
(22, '2025-01-21', 'PG343', 'Pembayaran gaji karyawan', 0, '2025-11-20 13:54:16.727815', NULL, 1),
(23, '2025-12-31', 'SW324', 'Sewa', 1, '2025-11-20 14:03:51.034612', NULL, 1),
(24, '2025-12-31', 'PS343', 'Penyusutan', 1, '2025-11-20 14:04:52.969520', NULL, 1);

-- --------------------------------------------------------

--
-- Table structure for table `accounting_journalline`
--

CREATE TABLE `accounting_journalline` (
  `id` bigint NOT NULL,
  `is_debit` tinyint(1) NOT NULL,
  `amount` decimal(18,2) NOT NULL,
  `tax_ppn` decimal(18,2) DEFAULT NULL,
  `account_id` bigint NOT NULL,
  `entry_id` bigint NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `accounting_journalline`
--

INSERT INTO `accounting_journalline` (`id`, `is_debit`, `amount`, `tax_ppn`, `account_id`, `entry_id`) VALUES
(25, 1, '50000000.00', NULL, 2, 13),
(26, 0, '50000000.00', NULL, 14, 13),
(27, 1, '20000000.00', NULL, 5, 14),
(28, 0, '20000000.00', NULL, 2, 14),
(29, 1, '5000000.00', NULL, 1, 15),
(30, 0, '5000000.00', NULL, 9, 15),
(31, 1, '12000000.00', NULL, 2, 16),
(32, 0, '12000000.00', NULL, 17, 16),
(33, 1, '3500000.00', NULL, 2, 17),
(34, 0, '3500000.00', NULL, 18, 17),
(35, 1, '2000000.00', NULL, 3, 18),
(36, 0, '2000000.00', NULL, 2, 18),
(37, 1, '5000000.00', NULL, 2, 19),
(38, 0, '5000000.00', NULL, 4, 19),
(39, 1, '5000000.00', NULL, 9, 20),
(40, 0, '5000000.00', NULL, 2, 20),
(41, 1, '2500000.00', NULL, 2, 21),
(42, 0, '2500000.00', NULL, 19, 21),
(43, 1, '6000000.00', NULL, 21, 22),
(44, 0, '6000000.00', NULL, 2, 22),
(45, 1, '1000000.00', NULL, 25, 23),
(46, 0, '1000000.00', NULL, 8, 23),
(47, 1, '2000000.00', NULL, 29, 24),
(48, 0, '2000000.00', NULL, 7, 24);

-- --------------------------------------------------------

--
-- Table structure for table `auth_group`
--

CREATE TABLE `auth_group` (
  `id` int NOT NULL,
  `name` varchar(150) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `auth_group_permissions`
--

CREATE TABLE `auth_group_permissions` (
  `id` bigint NOT NULL,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `auth_permission`
--

CREATE TABLE `auth_permission` (
  `id` int NOT NULL,
  `name` varchar(255) NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `auth_permission`
--

INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES
(1, 'Can add log entry', 1, 'add_logentry'),
(2, 'Can change log entry', 1, 'change_logentry'),
(3, 'Can delete log entry', 1, 'delete_logentry'),
(4, 'Can view log entry', 1, 'view_logentry'),
(5, 'Can add permission', 2, 'add_permission'),
(6, 'Can change permission', 2, 'change_permission'),
(7, 'Can delete permission', 2, 'delete_permission'),
(8, 'Can view permission', 2, 'view_permission'),
(9, 'Can add group', 3, 'add_group'),
(10, 'Can change group', 3, 'change_group'),
(11, 'Can delete group', 3, 'delete_group'),
(12, 'Can view group', 3, 'view_group'),
(13, 'Can add user', 4, 'add_user'),
(14, 'Can change user', 4, 'change_user'),
(15, 'Can delete user', 4, 'delete_user'),
(16, 'Can view user', 4, 'view_user'),
(17, 'Can add content type', 5, 'add_contenttype'),
(18, 'Can change content type', 5, 'change_contenttype'),
(19, 'Can delete content type', 5, 'delete_contenttype'),
(20, 'Can view content type', 5, 'view_contenttype'),
(21, 'Can add session', 6, 'add_session'),
(22, 'Can change session', 6, 'change_session'),
(23, 'Can delete session', 6, 'delete_session'),
(24, 'Can view session', 6, 'view_session'),
(25, 'Can add company', 7, 'add_company'),
(26, 'Can change company', 7, 'change_company'),
(27, 'Can delete company', 7, 'delete_company'),
(28, 'Can view company', 7, 'view_company'),
(29, 'Can add account', 8, 'add_account'),
(30, 'Can change account', 8, 'change_account'),
(31, 'Can delete account', 8, 'delete_account'),
(32, 'Can view account', 8, 'view_account'),
(33, 'Can add journal entry', 9, 'add_journalentry'),
(34, 'Can change journal entry', 9, 'change_journalentry'),
(35, 'Can delete journal entry', 9, 'delete_journalentry'),
(36, 'Can view journal entry', 9, 'view_journalentry'),
(37, 'Can add journal line', 10, 'add_journalline'),
(38, 'Can change journal line', 10, 'change_journalline'),
(39, 'Can delete journal line', 10, 'delete_journalline'),
(40, 'Can view journal line', 10, 'view_journalline'),
(41, 'Can add closing status', 11, 'add_closingstatus'),
(42, 'Can change closing status', 11, 'change_closingstatus'),
(43, 'Can delete closing status', 11, 'delete_closingstatus'),
(44, 'Can view closing status', 11, 'view_closingstatus');

-- --------------------------------------------------------

--
-- Table structure for table `auth_user`
--

CREATE TABLE `auth_user` (
  `id` int NOT NULL,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `auth_user`
--

INSERT INTO `auth_user` (`id`, `password`, `last_login`, `is_superuser`, `username`, `first_name`, `last_name`, `email`, `is_staff`, `is_active`, `date_joined`) VALUES
(1, 'pbkdf2_sha256$600000$dp7C6xd4ndpF67qON6ZBuN$RuVMbSRoYXQrxGfEwyIJD5eX4N5WXc+n2NNf/hGwVb8=', '2025-11-20 16:02:22.792177', 1, 'admin', '', '', 'admin.dpongs@gmail.com', 1, 1, '2025-11-17 09:12:24.000000');

-- --------------------------------------------------------

--
-- Table structure for table `auth_user_groups`
--

CREATE TABLE `auth_user_groups` (
  `id` bigint NOT NULL,
  `user_id` int NOT NULL,
  `group_id` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `auth_user_user_permissions`
--

CREATE TABLE `auth_user_user_permissions` (
  `id` bigint NOT NULL,
  `user_id` int NOT NULL,
  `permission_id` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `django_admin_log`
--

CREATE TABLE `django_admin_log` (
  `id` int NOT NULL,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint UNSIGNED NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` int NOT NULL
) ;

--
-- Dumping data for table `django_admin_log`
--

INSERT INTO `django_admin_log` (`id`, `action_time`, `object_id`, `object_repr`, `action_flag`, `change_message`, `content_type_id`, `user_id`) VALUES
(1, '2025-11-20 15:27:57.642524', '1', 'D\'Pongs Wisata Keluarga', 1, '[{\"added\": {}}]', 7, 1),
(2, '2025-11-20 15:38:18.955362', '1', 'admin', 2, '[{\"changed\": {\"fields\": [\"Email address\"]}}]', 4, 1);

-- --------------------------------------------------------

--
-- Table structure for table `django_content_type`
--

CREATE TABLE `django_content_type` (
  `id` int NOT NULL,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `django_content_type`
--

INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES
(8, 'accounting', 'account'),
(11, 'accounting', 'closingstatus'),
(7, 'accounting', 'company'),
(9, 'accounting', 'journalentry'),
(10, 'accounting', 'journalline'),
(1, 'admin', 'logentry'),
(3, 'auth', 'group'),
(2, 'auth', 'permission'),
(4, 'auth', 'user'),
(5, 'contenttypes', 'contenttype'),
(6, 'sessions', 'session');

-- --------------------------------------------------------

--
-- Table structure for table `django_migrations`
--

CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `django_migrations`
--

INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES
(1, 'contenttypes', '0001_initial', '2025-11-17 09:10:16.981359'),
(2, 'auth', '0001_initial', '2025-11-17 09:10:17.395478'),
(3, 'admin', '0001_initial', '2025-11-17 09:10:17.500973'),
(4, 'admin', '0002_logentry_remove_auto_add', '2025-11-17 09:10:17.507956'),
(5, 'admin', '0003_logentry_add_action_flag_choices', '2025-11-17 09:10:17.515951'),
(6, 'contenttypes', '0002_remove_content_type_name', '2025-11-17 09:10:17.592175'),
(7, 'auth', '0002_alter_permission_name_max_length', '2025-11-17 09:10:17.675577'),
(8, 'auth', '0003_alter_user_email_max_length', '2025-11-17 09:10:17.701507'),
(9, 'auth', '0004_alter_user_username_opts', '2025-11-17 09:10:17.708489'),
(10, 'auth', '0005_alter_user_last_login_null', '2025-11-17 09:10:17.755397'),
(11, 'auth', '0006_require_contenttypes_0002', '2025-11-17 09:10:17.758356'),
(12, 'auth', '0007_alter_validators_add_error_messages', '2025-11-17 09:10:17.766338'),
(13, 'auth', '0008_alter_user_username_max_length', '2025-11-17 09:10:17.830088'),
(14, 'auth', '0009_alter_user_last_name_max_length', '2025-11-17 09:10:17.892922'),
(15, 'auth', '0010_alter_group_name_max_length', '2025-11-17 09:10:17.918849'),
(16, 'auth', '0011_update_proxy_permissions', '2025-11-17 09:10:17.927826'),
(17, 'auth', '0012_alter_user_first_name_max_length', '2025-11-17 09:10:17.977725'),
(18, 'sessions', '0001_initial', '2025-11-17 09:10:18.010867'),
(19, 'accounting', '0001_initial', '2025-11-17 09:20:03.706704'),
(20, 'accounting', '0002_closingstatus', '2025-11-18 09:50:53.293078');

-- --------------------------------------------------------

--
-- Table structure for table `django_session`
--

CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `django_session`
--

INSERT INTO `django_session` (`session_key`, `session_data`, `expire_date`) VALUES
('6q8i15aziy4z6vt5rv91wn6qy49z9plc', '.eJxVjEEOwiAQRe_C2hBaOjPUpXvPQBgGpGpoUtqV8e7apAvd_vfefykftrX4raXFT6LOqlOn341DfKS6A7mHept1nOu6TKx3RR-06ess6Xk53L-DElr51jmxw2gsMUgcHY6AQoAB0VjGLGCBnEmRmAwMTJkg9hk7tkPuCVG9P96HN2Q:1vM770:cqDO8_zFOfqNFmnDBvKskCnkl1kPMDbx_SL7pcxqXLY', '2025-12-04 16:02:22.794419');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `accounting_account`
--
ALTER TABLE `accounting_account`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `code` (`code`);

--
-- Indexes for table `accounting_closingstatus`
--
ALTER TABLE `accounting_closingstatus`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `year` (`year`);

--
-- Indexes for table `accounting_company`
--
ALTER TABLE `accounting_company`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `accounting_journalentry`
--
ALTER TABLE `accounting_journalentry`
  ADD PRIMARY KEY (`id`),
  ADD KEY `accounting_journalen_company_id_9e360981_fk_accountin` (`company_id`),
  ADD KEY `accounting_journalentry_created_by_id_60f500e8_fk_auth_user_id` (`created_by_id`);

--
-- Indexes for table `accounting_journalline`
--
ALTER TABLE `accounting_journalline`
  ADD PRIMARY KEY (`id`),
  ADD KEY `accounting_journalli_account_id_2355bfed_fk_accountin` (`account_id`),
  ADD KEY `accounting_journalli_entry_id_a1a8fdef_fk_accountin` (`entry_id`);

--
-- Indexes for table `auth_group`
--
ALTER TABLE `auth_group`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`);

--
-- Indexes for table `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  ADD KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`);

--
-- Indexes for table `auth_permission`
--
ALTER TABLE `auth_permission`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`);

--
-- Indexes for table `auth_user`
--
ALTER TABLE `auth_user`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- Indexes for table `auth_user_groups`
--
ALTER TABLE `auth_user_groups`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  ADD KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`);

--
-- Indexes for table `auth_user_user_permissions`
--
ALTER TABLE `auth_user_user_permissions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  ADD KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`);

--
-- Indexes for table `django_admin_log`
--
ALTER TABLE `django_admin_log`
  ADD PRIMARY KEY (`id`),
  ADD KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  ADD KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`);

--
-- Indexes for table `django_content_type`
--
ALTER TABLE `django_content_type`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`);

--
-- Indexes for table `django_migrations`
--
ALTER TABLE `django_migrations`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `django_session`
--
ALTER TABLE `django_session`
  ADD PRIMARY KEY (`session_key`),
  ADD KEY `django_session_expire_date_a5c62663` (`expire_date`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `accounting_account`
--
ALTER TABLE `accounting_account`
  MODIFY `id` bigint NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=31;

--
-- AUTO_INCREMENT for table `accounting_closingstatus`
--
ALTER TABLE `accounting_closingstatus`
  MODIFY `id` bigint NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `accounting_company`
--
ALTER TABLE `accounting_company`
  MODIFY `id` bigint NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `accounting_journalentry`
--
ALTER TABLE `accounting_journalentry`
  MODIFY `id` bigint NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=26;

--
-- AUTO_INCREMENT for table `accounting_journalline`
--
ALTER TABLE `accounting_journalline`
  MODIFY `id` bigint NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=51;

--
-- AUTO_INCREMENT for table `auth_group`
--
ALTER TABLE `auth_group`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  MODIFY `id` bigint NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `auth_permission`
--
ALTER TABLE `auth_permission`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=45;

--
-- AUTO_INCREMENT for table `auth_user`
--
ALTER TABLE `auth_user`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `auth_user_groups`
--
ALTER TABLE `auth_user_groups`
  MODIFY `id` bigint NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `auth_user_user_permissions`
--
ALTER TABLE `auth_user_user_permissions`
  MODIFY `id` bigint NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `django_admin_log`
--
ALTER TABLE `django_admin_log`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `django_content_type`
--
ALTER TABLE `django_content_type`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT for table `django_migrations`
--
ALTER TABLE `django_migrations`
  MODIFY `id` bigint NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=21;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `accounting_journalentry`
--
ALTER TABLE `accounting_journalentry`
  ADD CONSTRAINT `accounting_journalen_company_id_9e360981_fk_accountin` FOREIGN KEY (`company_id`) REFERENCES `accounting_company` (`id`),
  ADD CONSTRAINT `accounting_journalentry_created_by_id_60f500e8_fk_auth_user_id` FOREIGN KEY (`created_by_id`) REFERENCES `auth_user` (`id`);

--
-- Constraints for table `accounting_journalline`
--
ALTER TABLE `accounting_journalline`
  ADD CONSTRAINT `accounting_journalli_account_id_2355bfed_fk_accountin` FOREIGN KEY (`account_id`) REFERENCES `accounting_account` (`id`),
  ADD CONSTRAINT `accounting_journalli_entry_id_a1a8fdef_fk_accountin` FOREIGN KEY (`entry_id`) REFERENCES `accounting_journalentry` (`id`);

--
-- Constraints for table `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  ADD CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  ADD CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`);

--
-- Constraints for table `auth_permission`
--
ALTER TABLE `auth_permission`
  ADD CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`);

--
-- Constraints for table `auth_user_groups`
--
ALTER TABLE `auth_user_groups`
  ADD CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  ADD CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);

--
-- Constraints for table `auth_user_user_permissions`
--
ALTER TABLE `auth_user_user_permissions`
  ADD CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  ADD CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);

--
-- Constraints for table `django_admin_log`
--
ALTER TABLE `django_admin_log`
  ADD CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  ADD CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
