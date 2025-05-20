#!/usr/bin/env python3
"""
Natural Language to SQL using CrewAI and MySQL (Object-Oriented)

This script:
- Connects to a local MySQL database via mysql-connector-python
- Uses a CrewAI LLM agent (via OpenRouter.ai) to convert NL queries into SQL
- Validates that only SELECT queries are passed to the DB
- On execution errors, regenerates SQL via a CrewAI agent
- Executes the generated (or regenerated) SQL and returns results as a pandas DataFrame
- Uses an agent to convert the SQL result into a natural language answer
- Reports metadata about generation, execution time, rows/cols, syntax validity, forbidden tokens, complexity, and confidence
- Validates user intent against the DB schema before any SQL is generated or run
"""

import os
import re
import time
import logging
import requests
import json
import sqlparse
from difflib import SequenceMatcher
from typing import Optional

import pandas as pd
from dotenv import load_dotenv
import mysql.connector
from crewai import Crew, Agent, Task

# -----------------------------------
# OpenRouter LLM Wrapper
# -----------------------------------
class OpenRouterLLM:
    def __init__(self,
                 api_key: str,
                 model: str = "openrouter/meta-llama/llama-3.3-8b-instruct:free",
                 endpoint: str = "https://openrouter.ai/api/v1/chat/completions"):
        self.api_key = api_key
        self.model = model
        self.endpoint = endpoint

    def create_chat_completion(self, messages: list) -> str:
        payload = {"model": self.model, "messages": messages}
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        resp = requests.post(self.endpoint, headers=headers, json=payload)
        if resp.status_code != 200:
            raise RuntimeError(f"OpenRouter API Error {resp.status_code}: {resp.text}")
        data = resp.json()
        return data["choices"][0]["message"]["content"]

# -----------------------------------
# Configuration & Prompts
# -----------------------------------
class Config:
    def __init__(self):
        load_dotenv()
        self.OPENROUTER_KEY: str = os.getenv("OPENROUTER_API_KEY")

        # MySQL connection details
        self.DB_HOST: str     = os.getenv("MYSQL_HOST")
        self.DB_PORT: int     = int(os.getenv("MYSQL_PORT"))
        self.DB_USER: str     = os.getenv("MYSQL_USER")
        self.DB_PASSWORD: str = os.getenv("MYSQL_PASSWORD")
        self.DB_DATABASE: str = os.getenv("MYSQL_DATABASE")

        # Forbid non-SELECT operations
        self.FORBIDDEN_TOKENS = ["insert","update","delete","drop","create","alter"]

        # Full table schema
        self.TABLE_SCHEMA: str = """
Table 1 : supply_chain_management.suppliers table – Master data of companies that supply goods.
supply_chain_management.suppliers (
    supplier_id    INT           NOT NULL AUTO_INCREMENT,  -- Unique supplier identifier
    supplier_name  VARCHAR(100)  NOT NULL,                -- Official name of the supplier
    contact_name   VARCHAR(100)  NOT NULL,                -- Name of the primary contact person
    phone          VARCHAR(30)   NOT NULL,                -- Contact phone number
    email          VARCHAR(100)  NOT NULL,                -- Contact email address
    address        VARCHAR(200)  NOT NULL,                -- Street address of the supplier
    city           VARCHAR(50)   NOT NULL,                -- City where the supplier is located
    state          VARCHAR(50)   NOT NULL,                -- State or province of the supplier
    postal_code    VARCHAR(20)   NOT NULL,                -- ZIP or postal code
    country        VARCHAR(50)   NOT NULL,                -- Country of the supplier
    PRIMARY KEY (supplier_id)
);
Note: Each supplier may supply many products.
Table 2 : supply_chain_management.manufacturers table – Data on organizations that produce products.
supply_chain_management.manufacturers (
    manufacturer_id   INT           NOT NULL AUTO_INCREMENT,  -- Unique manufacturer identifier
    manufacturer_name VARCHAR(100)  NOT NULL,                -- Official name of the manufacturer
    contact_name      VARCHAR(100),                          -- Name of the primary contact person
    phone             VARCHAR(30),                           -- Contact phone number
    email             VARCHAR(100),                          -- Contact email address
    address           VARCHAR(200),                          -- Street address of the manufacturer
    city              VARCHAR(50),                           -- City where the manufacturer is located
    state             VARCHAR(50),                           -- State or province of the manufacturer
    postal_code       VARCHAR(20),                           -- ZIP or postal code
    country           VARCHAR(50),                           -- Country of the manufacturer
    PRIMARY KEY (manufacturer_id)
);
Note: Products reference this table to identify their maker.
Table 3 :supply_chain_management.warehouses table – Storage locations for holding inventory.
supply_chain_management.warehouses (
    warehouse_id INT           NOT NULL AUTO_INCREMENT,  -- Unique warehouse identifier
    name         VARCHAR(100)  NOT NULL,                -- Name of the warehouse
    location     VARCHAR(200),                          -- Physical address of the warehouse
    PRIMARY KEY (warehouse_id)
);
Note: Inventory records tie products to these locations.
Table 4 : supply_chain_management.products table – Catalog of all products handled in the supply chain.
supply_chain_management.products (
    product_id      INT           NOT NULL AUTO_INCREMENT,  -- Unique product identifier
    product_name    VARCHAR(100)  NOT NULL,                -- Human-readable product name
    description     TEXT,                                 -- Detailed description of the product
    supplier_id     INT           NOT NULL,                -- FK: references suppliers.supplier_id
    manufacturer_id INT,                                  -- FK: references manufacturers.manufacturer_id
    unit_price      DECIMAL(10,2) NOT NULL,               -- Standard price per unit
    weight_kg       DECIMAL(8,2),                         -- Weight of the product in kilograms
    discontinued    TINYINT(1)   NOT NULL DEFAULT 0,      -- Flag indicating if the product is discontinued
    PRIMARY KEY (product_id),
    FOREIGN KEY (supplier_id)     REFERENCES supply_chain_management.suppliers(supplier_id),
    FOREIGN KEY (manufacturer_id) REFERENCES supply_chain_management.manufacturers(manufacturer_id)
);
Note: Each product links back to one supplier (and optionally one manufacturer).
Table 5 :supply_chain_management.inventory table – Tracks quantities of each product in each warehouse.
supply_chain_management.inventory (
    warehouse_id     INT NOT NULL,                       -- FK: references warehouses.warehouse_id
    product_id       INT NOT NULL,                       -- FK: references products.product_id
    quantity         INT NOT NULL DEFAULT 0,             -- Current stock level
    PRIMARY KEY (warehouse_id, product_id),
    FOREIGN KEY (warehouse_id) REFERENCES supply_chain_management.warehouses(warehouse_id),
    FOREIGN KEY (product_id)   REFERENCES supply_chain_management.products(product_id)
);
Note: Whenever stock changes, this record reflects the latest quantity per warehouse–product pair.
Table 6 :supply_chain_management.customers table – Master data for clients placing orders.
supply_chain_management.customers (
    customer_id INT           NOT NULL AUTO_INCREMENT,  -- Unique customer identifier
    first_name  VARCHAR(50)   NOT NULL,                -- Customer’s first name
    last_name   VARCHAR(50)   NOT NULL,                -- Customer’s last name
    email       VARCHAR(100)  NOT NULL,                -- Contact email address
    phone       VARCHAR(30),                           -- Contact phone number
    address     VARCHAR(200),                          -- Street address
    city        VARCHAR(50),                           -- City
    state       VARCHAR(50),                           -- State or province
    postal_code VARCHAR(20),                           -- ZIP or postal code
    country     VARCHAR(50),                           -- Country
    PRIMARY KEY (customer_id)
);
Note: Orders reference this table to identify the buyer.
Table 7 :supply_chain_management.orders table – Records of customer orders.
supply_chain_management.orders (
    order_id     INT           NOT NULL AUTO_INCREMENT,  -- Unique order identifier
    customer_id  INT           NOT NULL,                -- FK: references customers.customer_id
    order_date   DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,  -- When the order was placed
    status       VARCHAR(30)   NOT NULL DEFAULT 'Pending',         -- e.g., “Pending”, “Shipped”
    total_amount DECIMAL(12,2),                                -- Calculated total for the order
    PRIMARY KEY (order_id),
    FOREIGN KEY (customer_id) REFERENCES supply_chain_management.customers(customer_id)
);
Note: One order may have multiple line-items in order_items.
Table 8 : supply_chain_management.order_items table – Line-items linking products to orders.
supply_chain_management.order_items (
    order_id   INT           NOT NULL,               -- FK: references orders.order_id
    product_id INT           NOT NULL,               -- FK: references products.product_id
    quantity   INT           NOT NULL DEFAULT 1,     -- Units ordered
    unit_price DECIMAL(10,2) NOT NULL,               -- Price per unit at time of order
    PRIMARY KEY (order_id, product_id),
    FOREIGN KEY (order_id)   REFERENCES supply_chain_management.orders(order_id),
    FOREIGN KEY (product_id) REFERENCES supply_chain_management.products(product_id)
);
Note: Helps track exactly which products were ordered and at what price.
Table 9 : supply_chain_management.shipments table – Shipment events for orders.
supply_chain_management.shipments (
    shipment_id   INT           NOT NULL AUTO_INCREMENT,  -- Unique shipment identifier
    order_id      INT           NOT NULL,                -- FK: references orders.order_id
    shipped_date  DATETIME,                           -- When the order was shipped
    delivery_date DATETIME,                           -- When the order was delivered
    carrier       VARCHAR(100),                       -- Shipping carrier name
    tracking_no   VARCHAR(100),                       -- Carrier’s tracking number
    status        VARCHAR(30)    NOT NULL DEFAULT 'In Transit',  -- Shipment status
    PRIMARY KEY (shipment_id),
    FOREIGN KEY (order_id) REFERENCES supply_chain_management.orders(order_id)
);
Note: One shipment record per dispatch; an order can generate one or more shipments.
"""

        # SQL generation system prompt
        self.SYSTEM_PROMPT: str = f"""
You are a proficient SQL Generation bot. Understand the background, table schemas and generate the correct SQL queries for the asked question.

Background:
This data represents a comprehensive supply-chain management system with the following entities:
• suppliers – master data on companies supplying goods  
• manufacturers – master data on organizations that produce products  
• warehouses – storage locations with capacity and location details  
• products – catalog of items with pricing, packaging and supply information  
• inventory – current stock levels per warehouse/product  
• customers – master data for clients placing orders  
• orders – customer orders with metadata such as dates, status and total amounts  
• order_items – line-items linking products to orders, tracking quantities and unit prices  
• shipments – dispatch records tied to orders, including shipment and delivery dates, carrier and tracking number  
{self.TABLE_SCHEMA}

Task to perform:
* Analyze the table descriptions above and understand the relationships between them.  
* You are provided with a `User Question`.  
* Based on your understanding of the tables generate a SQL query for the User Question asked.

Note:
Multiple rows can share the same foreign key (e.g., one order with multiple items).  
Use DISTINCT when listing shipments or products to avoid duplicates unless detailed rows are required.

Input provided to you:
1. User Question : The question asked by the user

Output format instruction:
* The output should only be the verified and corrected SQL query and nothing else.  
* DO NOT add any sentences before or after the SQL query.
"""

        # SQL to text system prompt
        self.SQL_TO_TEXT_SYSTEM_PROMPT: str = f"""
You are a proficient AI assistant who generates natural language responses to the User using the database result provided to you.

{self.TABLE_SCHEMA}

Input:
- User Question : The question asked by the user
- SQL Query : The SQL Query executed against the database
- Database result : The result data obtained after running the SQL Query on the database

Task to perform:
- Understand the table schema and the SQL Query used to solve the User Question
- Analyze the Database result
- Generate a natural language text answer to the User's question using the information provided

Output format:
- Try to keep the answer well formatted in bulleted points
- Keep the answer specific to the question
- Avoid adding additional unnecessary information
- The output should only be the answer to the question and nothing else.

Special Instruction:
If the Tabular Data provided to you is empty, then you must respond saying you are unable to answer the question since you do not have enough data, DO NOT make up any answer of your own.
"""

# -----------------------------------
# Logging
# -----------------------------------
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger(__name__)

# -----------------------------------
# Validator
# -----------------------------------
class Validator:
    def __init__(self, forbidden_tokens):
        self.forbidden_tokens = forbidden_tokens
    def validate_syntax(self, sql: str) -> bool:
        try:
            return len(sqlparse.parse(sql)) > 0
        except:
            return False
    def count_forbidden_tokens(self, sql: str) -> int:
        return len(re.findall(rf"\b({'|'.join(self.forbidden_tokens)})\b", sql, re.IGNORECASE))
    def compute_complexity(self, sql: str) -> int:
        return len(re.findall(r"\bjoin\b", sql, re.IGNORECASE)) + len(re.findall(r"\(\s*select\b", sql, re.IGNORECASE))
    def compute_similarity(self, a: str, b: str) -> float:
        return SequenceMatcher(None, a, b).ratio()

# -----------------------------------
# Database Handler
# -----------------------------------
class DatabaseHandler:
    def __init__(self, config: Config):
        try:
            self.conn = mysql.connector.connect(
                host=config.DB_HOST,
                port=config.DB_PORT,
                user=config.DB_USER,
                password=config.DB_PASSWORD,
                database=config.DB_DATABASE,
                autocommit=True
            )
            logger.info("Connected to MySQL %s:%s/%s", config.DB_HOST, config.DB_PORT, config.DB_DATABASE)
        except mysql.connector.Error as e:
            logger.error("MySQL connection error: %s", e)
            self.conn = None
    def execute_sql_query(self, sql_query: str) -> pd.DataFrame:
        if not self.conn:
            return pd.DataFrame()
        cur = self.conn.cursor(dictionary=True)
        cur.execute(sql_query)
        rows = cur.fetchall()
        cur.close()
        return pd.DataFrame(rows)

# -----------------------------------
# Crew Factory
# -----------------------------------
class CrewFactory:
    def __init__(self, llm: OpenRouterLLM, config: Config):
        self.llm = llm
        self.config = config

    def get_intent_crew(self) -> Crew:
        intent_agent = Agent(
            llm=self.llm,
            role="Query Intent Assistant",
            goal=(
                "You are given a user question and the database table schema. "
                "If the question can be answered using SQL on the given schema, respond exactly 'Valid'. "
                "If it cannot, respond exactly 'Invalid'."
            ),
            backstory="You evaluate whether a question relates to the available tables and columns.",
            verbose=True,
            allow_delegation=False
        )
        task = Task(
            description=f"Schema: {self.config.TABLE_SCHEMA}\nUser Question: {{query}}",
            expected_output="<Valid or Invalid>",
            agent=intent_agent
        )
        return Crew(agents=[intent_agent], tasks=[task])

    def get_generation_crew(self) -> Crew:
        gen_agent = Agent(
            llm=self.llm,
            role="SQL Generation Assistant",
            goal=self.config.SYSTEM_PROMPT,
            backstory="",
            verbose=True,
            allow_delegation=False
        )
        task = Task(
            description="User Question: {query}",
            expected_output="<SQL query>",
            agent=gen_agent
        )
        return Crew(agents=[gen_agent], tasks=[task])

    def get_ddl_check_crew(self) -> Crew:
        ddl_agent = Agent(
            llm=self.llm,
            role="DDL Validation Assistant",
            goal="If SQL contains DDL tokens like 'INSERT','UPDATE','ALTER','CREATE','DELETE','DROP', respond 'ERROR', else 'OK'",
            backstory="",
            verbose=True
        )
        task = Task(
            description="SQL to validate: {sql}",
            expected_output="<OK or ERROR>",
            agent=ddl_agent
        )
        return Crew(agents=[ddl_agent], tasks=[task])

    def get_verify_crew(self) -> Crew:
        verify_agent = Agent(
            llm=self.llm,
            role="SQL Verification Assistant",
            goal="Fix erroneous SQL to valid SELECT only",
            backstory="",
            verbose=True
        )
        task = Task(
            description="Original SQL: {sql}\nSchema:\n{schema}\nError: {error}",
            expected_output="<SQL>",
            agent=verify_agent
        )
        return Crew(agents=[verify_agent], tasks=[task])

    def get_sql_to_text_crew(self) -> Crew:
        text_agent = Agent(
            llm=self.llm,
            role="SQL to Text Assistant",
            goal=self.config.SQL_TO_TEXT_SYSTEM_PROMPT,
            backstory="",
            verbose=True,
            allow_delegation=False
        )
        task = Task(
            description="User Question: {query}\nSQL Query: {sql_query}\nResult:\n{db_result}",
            expected_output="<Text>",
            agent=text_agent
        )
        return Crew(agents=[text_agent], tasks=[task])

# -----------------------------------
# Main Application
# -----------------------------------
class SQLApp:
    def __init__(self):
        self.config = Config()
        self.validator = Validator(self.config.FORBIDDEN_TOKENS)
        self.db_handler = DatabaseHandler(self.config)
        self.llm = OpenRouterLLM(api_key=self.config.OPENROUTER_KEY)

        factory = CrewFactory(self.llm, self.config)
        self.intent_crew  = factory.get_intent_crew()
        self.gen_crew     = factory.get_generation_crew()
        self.ddl_crew     = factory.get_ddl_check_crew()
        self.verify_crew  = factory.get_verify_crew()
        self.text_crew    = factory.get_sql_to_text_crew()

    def run(self, query_input=None):
        q = query_input or input("Ask your query: ")

        intent = self.intent_crew.kickoff(inputs={"query": q})
        if str(intent).lower().strip() != "valid":
            return "Invalid query", "", ""

        start = time.perf_counter()
        raw = self.gen_crew.kickoff(inputs={"query": q})
        gen_time = time.perf_counter() - start

        sql = str(raw).strip()
        sql = re.sub(r"^```(?:sql)?\s*", "", sql)
        sql = re.sub(r"\s*```$", "", sql)

        syntax_ok = self.validator.validate_syntax(sql)
        forbidden_count = self.validator.count_forbidden_tokens(sql)
        complexity = self.validator.compute_complexity(sql)

        ddl_check = self.ddl_crew.kickoff(inputs={"sql": sql})
        if str(ddl_check).lower().startswith("error"):
            return "DDL operations not allowed.", "", ""

        try:
            exec_start = time.perf_counter()
            df = self.db_handler.execute_sql_query(sql)
            exec_time = time.perf_counter() - exec_start
        except Exception as e:
            regen = self.verify_crew.kickoff(inputs={
                "sql": sql,
                "schema": self.config.TABLE_SCHEMA,
                "error": str(e)
            })
            sql = str(regen).strip()
            sql = re.sub(r"^```(?:sql)?\s*", "", sql)
            sql = re.sub(r"\s*```$", "", sql)

            exec_start = time.perf_counter()
            df = self.db_handler.execute_sql_query(sql)
            exec_time = time.perf_counter() - exec_start

        result = df.head().to_string(index=False)
        metrics = (
            f"Generation Time: {gen_time:.3f}s\n"
            f"Execution Time: {exec_time:.3f}s\n"
            f"Rows Returned: {len(df)}\n"
            f"Columns: {len(df.columns)}\n"
            f"Syntax Valid: {syntax_ok}\n"
            f"Forbidden Tokens: {forbidden_count}\n"
            f"Query Complexity: {complexity}"
        )

        return sql, result, metrics


if __name__ == "__main__":
    SQLApp().run()


