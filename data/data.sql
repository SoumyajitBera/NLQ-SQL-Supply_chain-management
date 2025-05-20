-- 1. Suppliers
INSERT INTO `suppliers` (
  `supplier_id`, `supplier_name`, `contact_name`, `phone`, `email`,
  `address`, `city`, `state`, `postal_code`, `country`
) VALUES
  (1, 'Acme Supplies',        'Alice Johnson', '555-1234', 'alice.johnson@acmesupplies.com',
     '123 Maple Street',       'Springfield',   'IL',   '62701', 'USA'),
  (2, 'Global Traders',       'Bob Smith',     '555-5678', 'bob.smith@globaltraders.com',
     '456 Oak Avenue',         'Metropolis',    'NY',   '10001', 'USA'),
  (3, 'Industrial Goods Co.', 'Carol Lee',     '555-9012', 'carol.lee@industrialgoods.com',
     '789 Pine Road',          'Gotham',        'NJ',   '07097', 'USA');

-- 2. Manufacturers
INSERT INTO `manufacturers` (
  `manufacturer_id`, `manufacturer_name`, `contact_name`, `phone`, `email`,
  `address`, `city`, `state`, `postal_code`, `country`
) VALUES
  (1, 'Widget Makers Inc.',     'David Wang',   '555-2220', 'd.wang@widgetmakers.com',
     '10 Industrial Parkway',    'Springfield',  'IL',  '62703', 'USA'),
  (2, 'Gadget Builders Ltd.',   'Eva Martinez', '555-3330', 'eva.martinez@gadgetbuilders.com',
     '55 Innovation Drive',      'Metropolis',   'NY',  '10003', 'USA');

-- 3. Warehouses
INSERT INTO `warehouses` (
  `warehouse_id`, `name`,               `location`
) VALUES
  (1, 'Central Warehouse', '100 Warehouse Lane, Springfield, IL'),
  (2, 'East Warehouse',    '200 Storage St, Metropolis, NY');

-- 4. Customers
INSERT INTO `customers` (
  `customer_id`, `first_name`, `last_name`, `email`,               `phone`,
  `address`,          `city`,        `state`, `postal_code`, `country`
) VALUES
  (1, 'John',  'Doe',   'john.doe@example.com',   '555-1111',
     '100 Elm St',    'Springfield', 'IL',   '62702', 'USA'),
  (2, 'Jane',  'Smith', 'jane.smith@example.com', '555-2222',
     '200 Birch Rd',  'Metropolis',  'NY',   '10002', 'USA'),
  (3, 'Emily', 'Davis', 'emily.davis@example.com','555-3333',
     '300 Cedar Blvd','Gotham',      'NJ',   '07098', 'USA');

-- 5. Products
INSERT INTO `products` (
  `product_id`, `product_name`, `description`,         `supplier_id`,
  `manufacturer_id`, `unit_price`, `weight_kg`, `discontinued`
) VALUES
  (1, 'Widget A', 'Standard widget',           1, 1, 15.50, 0.50, 0),
  (2, 'Gadget B', 'Advanced gadget',           2, 2, 23.75, 1.20, 0),
  (3, 'Component C', 'Electronic component',   3, 1, 42.00, 0.10, 0),
  (4, 'Device D', 'High-end device',           2, 2, 75.00, 2.00, 0),
  (5, 'Legacy Widget', 'Discontinued legacy',  1, 1,  9.99, 0.30, 1);

-- 6. Orders
INSERT INTO `orders` (
  `order_id`, `customer_id`, `order_date`,           `status`, `total_amount`
) VALUES
  (1, 1, '2025-05-10 09:15:00', 'Shipped', 365.00),
  (2, 2, '2025-05-11 14:40:00', 'Pending', 221.25),
  (3, 3, '2025-05-12 16:20:00', 'Pending', 106.00);

-- 7. Inventory
INSERT INTO `inventory` (
  `warehouse_id`, `product_id`, `quantity`
) VALUES
  (1, 1, 100),
  (1, 3,  50),
  (1, 5,   0),
  (2, 2,  75),
  (2, 4,  20);

-- 8. Order Items
INSERT INTO `order_items` (
  `order_id`, `product_id`, `quantity`, `unit_price`
) VALUES
  (1, 1, 10, 15.50),
  (1, 3,  5, 42.00),
  (2, 2,  3, 23.75),
  (2, 4,  2, 75.00),
  (3, 1,  2, 15.50),
  (3, 4,  1, 75.00);

-- 9. Shipments
INSERT INTO `shipments` (
  `shipment_id`, `order_id`, `shipped_date`,        `delivery_date`,
  `carrier`,         `tracking_no`,     `status`
) VALUES
  (1, 1, '2025-05-11 10:00:00', '2025-05-14 12:00:00',
      'Speedy Express', 'SE123456789', 'Delivered'),
  (2, 3, '2025-05-13 09:00:00', NULL,
      'Global Shipping','GS987654321','In Transit');
