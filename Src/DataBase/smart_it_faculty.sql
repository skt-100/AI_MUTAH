-- ============================================================
-- Database: smart_it_faculty
-- ============================================================

CREATE DATABASE IF NOT EXISTS `smart_it_faculty`
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE `smart_it_faculty`;

-- ------------------------------------------------------------
-- Table: students
-- ------------------------------------------------------------
CREATE TABLE `students` (
  `student_id`      bigint unsigned   NOT NULL,
  `full_name`       varchar(100)      COLLATE utf8mb4_unicode_ci NOT NULL,
  `email`           varchar(100)      COLLATE utf8mb4_unicode_ci NOT NULL,
  `password`        varchar(60)       COLLATE utf8mb4_unicode_ci NOT NULL,
  `academic_year`   tinyint unsigned  NOT NULL DEFAULT '1',
  `gpa`             decimal(4,2)      NOT NULL DEFAULT '0.00',
  `completed_hours` tinyint unsigned  NOT NULL DEFAULT '0',
  `specialization`  varchar(100)      COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`student_id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------
-- Table: faculties
-- ------------------------------------------------------------
CREATE TABLE `faculties` (
  `faculty_id`   int unsigned  NOT NULL AUTO_INCREMENT,
  `faculty_name` varchar(150)  COLLATE utf8mb4_unicode_ci NOT NULL,
  `icon_path`    varchar(255)  COLLATE utf8mb4_unicode_ci NOT NULL,
  `description`  text          COLLATE utf8mb4_unicode_ci NOT NULL,
  `founded_year` varchar(50)   COLLATE utf8mb4_unicode_ci NOT NULL,
  `dept_label`   varchar(50)   COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_featured`  tinyint(1)    DEFAULT '0',
  PRIMARY KEY (`faculty_id`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------
-- Table: instructors
-- ------------------------------------------------------------
CREATE TABLE `instructors` (
  `instructor_id`  smallint unsigned NOT NULL AUTO_INCREMENT,
  `full_name`      varchar(100)      COLLATE utf8mb4_unicode_ci NOT NULL,
  `email`          varchar(100)      COLLATE utf8mb4_unicode_ci NOT NULL,
  `password`       varchar(10)       COLLATE utf8mb4_unicode_ci NOT NULL,
  `specialization` varchar(100)      COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `academic_rank`  varchar(50)       COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`instructor_id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=40 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------
-- Table: courses
-- ------------------------------------------------------------
CREATE TABLE `courses` (
  `course_id`      int unsigned NOT NULL,
  `course_name`    varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `credit_hours`   tinyint unsigned NOT NULL DEFAULT '3',
  `prerequisite`   int unsigned DEFAULT NULL,
  `specialization` enum(
    'الذكاء الاصطناعي وعلم البيانات',
    'هندسة البرمجيات',
    'علم الحاسوب',
    'امن معلومات',
    'نظم معلومات حاسوبية',
    'مشترك'
  ) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`course_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------
-- Table: sections
-- ------------------------------------------------------------
CREATE TABLE `sections` (
  `section_id`     int unsigned      NOT NULL AUTO_INCREMENT,
  `course_id`      int unsigned      NOT NULL,
  `instructor_id`  smallint unsigned DEFAULT NULL,
  `section_number` tinyint unsigned  NOT NULL,
  `days`           varchar(50)       COLLATE utf8mb4_unicode_ci NOT NULL,
  `start_time`     time              NOT NULL,
  `end_time`       time              NOT NULL,
  `room`           varchar(50)       COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `capacity`       smallint unsigned NOT NULL DEFAULT '25',
  `status`         enum('مفتوح','مغلق') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'مفتوح',
  PRIMARY KEY (`section_id`),
  KEY `course_number`   (`course_id`),
  KEY `sections_ibfk_2` (`instructor_id`),
  CONSTRAINT `sections_ibfk_1` FOREIGN KEY (`course_id`)     REFERENCES `courses`     (`course_id`),
  CONSTRAINT `sections_ibfk_2` FOREIGN KEY (`instructor_id`) REFERENCES `instructors` (`instructor_id`)
) ENGINE=InnoDB AUTO_INCREMENT=205 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------
-- Table: enrollments
-- ------------------------------------------------------------
CREATE TABLE `enrollments` (
  `enrollment_id` int unsigned    NOT NULL AUTO_INCREMENT,
  `student_id`    bigint unsigned NOT NULL,
  `section_id`    int unsigned    NOT NULL,
  `enrolled_at`   datetime        NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`enrollment_id`),
  KEY `student_id` (`student_id`),
  KEY `section_id` (`section_id`),
  CONSTRAINT `enrollments_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `students` (`student_id`),
  CONSTRAINT `enrollments_ibfk_2` FOREIGN KEY (`section_id`) REFERENCES `sections` (`section_id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------
-- Table: attendance
-- ------------------------------------------------------------
CREATE TABLE `attendance` (
  `student_id`     bigint unsigned   NOT NULL,
  `section_id`     int unsigned      NOT NULL,
  `absences_count` tinyint unsigned  DEFAULT '0',
  PRIMARY KEY (`student_id`, `section_id`),
  KEY `section_id` (`section_id`),
  CONSTRAINT `attendance_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `students`  (`student_id`) ON DELETE CASCADE,
  CONSTRAINT `attendance_ibfk_2` FOREIGN KEY (`section_id`) REFERENCES `sections`  (`section_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------
-- Table: grades
-- ------------------------------------------------------------
CREATE TABLE `grades` (
  `student_id`          bigint unsigned NOT NULL,
  `section_id`          int unsigned    NOT NULL,
  `participation_grade` decimal(4,2)    DEFAULT '0.00',
  `midterm_grade`       decimal(4,2)    DEFAULT '0.00',
  `final_grade`         decimal(4,2)    DEFAULT '0.00',
  PRIMARY KEY (`student_id`, `section_id`),
  KEY `section_id` (`section_id`),
  CONSTRAINT `grades_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `students` (`student_id`) ON DELETE CASCADE,
  CONSTRAINT `grades_ibfk_2` FOREIGN KEY (`section_id`) REFERENCES `sections` (`section_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------
-- Table: student_records
-- ------------------------------------------------------------
CREATE TABLE `student_records` (
  `record_id`   int unsigned    NOT NULL AUTO_INCREMENT,
  `student_id`  bigint unsigned NOT NULL,
  `course_id`   int unsigned    NOT NULL,
  `final_grade` decimal(4,2)    NOT NULL DEFAULT '0.00',
  PRIMARY KEY (`record_id`),
  KEY `student_id`    (`student_id`),
  KEY `course_number` (`course_id`),
  CONSTRAINT `student_records_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `students` (`student_id`),
  CONSTRAINT `student_records_ibfk_2` FOREIGN KEY (`course_id`)  REFERENCES `courses`  (`course_id`)
) ENGINE=InnoDB AUTO_INCREMENT=615 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------
-- Table: notifications
-- ------------------------------------------------------------
CREATE TABLE `notifications` (
  `notification_id` int unsigned    NOT NULL AUTO_INCREMENT,
  `student_id`      bigint unsigned NOT NULL,
  `section_id`      int unsigned    NOT NULL,
  `change_type`     enum('وقت','قاعة','مدرس','يوم') COLLATE utf8mb4_unicode_ci NOT NULL,
  `old_value`       varchar(100)    COLLATE utf8mb4_unicode_ci NOT NULL,
  `new_value`       varchar(100)    COLLATE utf8mb4_unicode_ci NOT NULL,
  `message`         text            COLLATE utf8mb4_unicode_ci NOT NULL,
  `sent_at`         datetime        NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`notification_id`),
  KEY `student_id` (`student_id`),
  KEY `section_id` (`section_id`),
  CONSTRAINT `notifications_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `students` (`student_id`),
  CONSTRAINT `notifications_ibfk_2` FOREIGN KEY (`section_id`) REFERENCES `sections` (`section_id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------
-- Table: registration_requests
-- ------------------------------------------------------------
CREATE TABLE `registration_requests` (
  `request_id`     int unsigned    NOT NULL AUTO_INCREMENT,
  `student_id`     bigint unsigned NOT NULL,
  `section_id`     int unsigned    NOT NULL,
  `priority_score` decimal(6,4)    NOT NULL DEFAULT '0.0000',
  `status`         enum('معلق','مقبول','مرفوض') NOT NULL DEFAULT 'معلق',
  `created_at`     datetime        NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`request_id`),
  KEY `student_id` (`student_id`),
  KEY `section_id` (`section_id`),
  CONSTRAINT `registration_requests_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `students` (`student_id`) ON DELETE CASCADE,
  CONSTRAINT `registration_requests_ibfk_2` FOREIGN KEY (`section_id`) REFERENCES `sections` (`section_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ------------------------------------------------------------
-- Table: section_requests
-- ------------------------------------------------------------
CREATE TABLE `section_requests` (
  `expansion_id` int unsigned    NOT NULL AUTO_INCREMENT,
  `student_id`   bigint unsigned NOT NULL,
  `section_id`   int unsigned    NOT NULL,
  `reason`       text            DEFAULT NULL,
  `status`       enum('معلق','مقبول','مرفوض') NOT NULL DEFAULT 'معلق',
  `created_at`   datetime        NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`expansion_id`),
  KEY `student_id` (`student_id`),
  KEY `section_id` (`section_id`),
  CONSTRAINT `section_requests_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `students` (`student_id`) ON DELETE CASCADE,
  CONSTRAINT `section_requests_ibfk_2` FOREIGN KEY (`section_id`) REFERENCES `sections` (`section_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ------------------------------------------------------------
-- View: honor_board
-- ------------------------------------------------------------
CREATE OR REPLACE ALGORITHM=UNDEFINED
  DEFINER=`sofyan`@`localhost`
  SQL SECURITY DEFINER
VIEW `honor_board` AS
  SELECT
    `students`.`student_id`       AS `student_id`,
    `students`.`full_name`        AS `full_name`,
    `students`.`completed_hours`  AS `completed_hours`,
    `students`.`gpa`              AS `gpa`,
    `students`.`specialization`   AS `specialization`,
    ROW_NUMBER() OVER (
      PARTITION BY `students`.`specialization`
      ORDER BY `students`.`gpa` DESC, `students`.`completed_hours` DESC
    ) AS `student_rank`
  FROM `students`
  WHERE `students`.`gpa` > 84.00;
