-- supply_chain_management_schema.sql

-- 1. Create database
CREATE DATABASE IF NOT EXISTS `supply_chain_management`
  DEFAULT CHARACTER SET = utf8mb4
  DEFAULT COLLATE = utf8mb4_unicode_ci;
USE `supply_chain_management`;

-- 2. suppliers: master data of companies that supply goods
CREATE TABLE IF NOT EXISTS `suppliers` (
  `supplier_id`   INT           NOT NULL AUTO_INCREMENT,
  `supplier_name` VARCHAR(100)  NOT NULL,
  `contact_name`  VARCHAR(100)  NOT NULL,
  `phone`         VARCHAR(30)   NOT NULL,
  `email`         VARCHAR(100)  NOT NULL,
  `address`       VARCHAR(200)  NOT NULL,
  `city`          VARCHAR(50)   NOT NULL,
  `state`         VARCHAR(50)   NOT NULL,
  `postal_code`   VARCHAR(20)   NOT NULL,
  `country`       VARCHAR(50)   NOT NULL,
  PRIMARY KEY (`supplier_id`)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;

-- 3. manufacturers: data on organizations that produce products
CREATE TABLE IF NOT EXISTS `manufacturers` (
  `manufacturer_id`   INT           NOT NULL AUTO_INCREMENT,
  `manufacturer_name` VARCHAR(100)  NOT NULL,
  `contact_name`      VARCHAR(100),
  `phone`             VARCHAR(30),
  `email`             VARCHAR(100),
  `address`           VARCHAR(200),
  `city`              VARCHAR(50),
  `state`             VARCHAR(50),
  `postal_code`       VARCHAR(20),
  `country`           VARCHAR(50),
  PRIMARY KEY (`manufacturer_id`)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;

-- 4. warehouses: storage locations for holding inventory
CREATE TABLE IF NOT EXISTS `warehouses` (
  `warehouse_id` INT           NOT NULL AUTO_INCREMENT,
  `name`         VARCHAR(100)  NOT NULL,
  `location`     VARCHAR(200),
  PRIMARY KEY (`warehouse_id`)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;

-- 5. customers: master data for clients placing orders
CREATE TABLE IF NOT EXISTS `customers` (
  `customer_id` INT           NOT NULL AUTO_INCREMENT,
  `first_name`  VARCHAR(50)   NOT NULL,
  `last_name`   VARCHAR(50)   NOT NULL,
  `email`       VARCHAR(100)  NOT NULL,
  `phone`       VARCHAR(30),
  `address`     VARCHAR(200),
  `city`        VARCHAR(50),
  `state`       VARCHAR(50),
  `postal_code` VARCHAR(20),
  `country`     VARCHAR(50),
  PRIMARY KEY (`customer_id`)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;

-- 6. products: catalog of all products handled in the supply chain
CREATE TABLE IF NOT EXISTS `products` (
  `product_id`      INT           NOT NULL AUTO_INCREMENT,
  `product_name`    VARCHAR(100)  NOT NULL,
  `description`     TEXT,
  `supplier_id`     INT           NOT NULL,
  `manufacturer_id` INT,
  `unit_price`      DECIMAL(10,2) NOT NULL,
  `weight_kg`       DECIMAL(8,2),
  `discontinued`    TINYINT(1)    NOT NULL DEFAULT 0,
  PRIMARY KEY (`product_id`),
  INDEX (`supplier_id`),
  INDEX (`manufacturer_id`),
  CONSTRAINT `fk_products_suppliers`
    FOREIGN KEY (`supplier_id`)
    REFERENCES `suppliers` (`supplier_id`),
  CONSTRAINT `fk_products_manufacturers`
    FOREIGN KEY (`manufacturer_id`)
    REFERENCES `manufacturers` (`manufacturer_id`)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;

-- 7. orders: records of customer orders
CREATE TABLE IF NOT EXISTS `orders` (
  `order_id`     INT           NOT NULL AUTO_INCREMENT,
  `customer_id`  INT           NOT NULL,
  `order_date`   DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `status`       VARCHAR(30)   NOT NULL DEFAULT 'Pending',
  `total_amount` DECIMAL(12,2),
  PRIMARY KEY (`order_id`),
  INDEX (`customer_id`),
  CONSTRAINT `fk_orders_customers`
    FOREIGN KEY (`customer_id`)
    REFERENCES `customers` (`customer_id`)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;

-- 8. inventory: tracks quantities of each product in each warehouse
CREATE TABLE IF NOT EXISTS `inventory` (
  `warehouse_id` INT NOT NULL,
  `product_id`   INT NOT NULL,
  `quantity`     INT NOT NULL DEFAULT 0,
  PRIMARY KEY (`warehouse_id`, `product_id`),
  INDEX (`product_id`),
  CONSTRAINT `fk_inventory_warehouses`
    FOREIGN KEY (`warehouse_id`)
    REFERENCES `warehouses` (`warehouse_id`),
  CONSTRAINT `fk_inventory_products`
    FOREIGN KEY (`product_id`)
    REFERENCES `products` (`product_id`)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;

-- 9. order_items: line-items linking products to orders
CREATE TABLE IF NOT EXISTS `order_items` (
  `order_id`   INT           NOT NULL,
  `product_id` INT           NOT NULL,
  `quantity`   INT           NOT NULL DEFAULT 1,
  `unit_price` DECIMAL(10,2) NOT NULL,
  PRIMARY KEY (`order_id`, `product_id`),
  INDEX (`product_id`),
  CONSTRAINT `fk_order_items_orders`
    FOREIGN KEY (`order_id`)
    REFERENCES `orders` (`order_id`),
  CONSTRAINT `fk_order_items_products`
    FOREIGN KEY (`product_id`)
    REFERENCES `products` (`product_id`)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;

-- 10. shipments: shipment events for orders
CREATE TABLE IF NOT EXISTS `shipments` (
  `shipment_id`   INT           NOT NULL AUTO_INCREMENT,
  `order_id`      INT           NOT NULL,
  `shipped_date`  DATETIME,
  `delivery_date` DATETIME,
  `carrier`       VARCHAR(100),
  `tracking_no`   VARCHAR(100),
  `status`        VARCHAR(30)   NOT NULL DEFAULT 'In Transit',
  PRIMARY KEY (`shipment_id`),
  INDEX (`order_id`),
  CONSTRAINT `fk_shipments_orders`
    FOREIGN KEY (`order_id`)
    REFERENCES `orders` (`order_id`)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;
