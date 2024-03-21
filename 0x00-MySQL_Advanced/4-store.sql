--  creates a trigger that decreases the quantity of an item after adding a new order.

-- CREATE TRIGGER ins_sum BEFORE INSERT ON account
    -- -> FOR EACH ROW SET @sum = @sum + NEW.amount;
CREATE TRIGGER order_trigger
AFTER INSERT ON orders
FOR EACH ROW
UPDATE items SET quantity = quantity - NEW.NUMBER
WHERE name = NEW.item_name;
