/* Read-only RFM-style segmentation. customer_key = 0 returns the portfolio. */
DECLARE @CustomerKey int = {{ Math.max(0, Number($json.customer_key || 0)) }};
DECLARE @TopN int = {{ Math.min(100, Math.max(1, Number($json.top_n || 25))) }};

WITH LastWarehouseDate AS (
    SELECT MAX(d.FullDateAlternateKey) AS AsOfDate
    FROM dbo.FactInternetSales s JOIN dbo.DimDate d ON d.DateKey = s.OrderDateKey
), CustomerMetrics AS (
    SELECT c.CustomerKey,
           CONCAT(c.FirstName, ' ', c.LastName) AS CustomerName,
           MAX(d.FullDateAlternateKey) AS LastPurchaseDate,
           DATEDIFF(day, MAX(d.FullDateAlternateKey), a.AsOfDate) AS RecencyDays,
           COUNT(DISTINCT s.SalesOrderNumber) AS OrderCount,
           SUM(CAST(s.SalesAmount AS decimal(19,2))) AS TotalSpend
    FROM dbo.DimCustomer c
    JOIN dbo.FactInternetSales s ON s.CustomerKey = c.CustomerKey
    JOIN dbo.DimDate d ON d.DateKey = s.OrderDateKey
    CROSS JOIN LastWarehouseDate a
    GROUP BY c.CustomerKey, c.FirstName, c.LastName, a.AsOfDate
), FavoriteCategory AS (
    SELECT CustomerKey, ProductCategory
    FROM (
        SELECT s.CustomerKey,
               COALESCE(pc.EnglishProductCategoryName, 'Uncategorized') AS ProductCategory,
               SUM(s.SalesAmount) AS CategorySpend,
               ROW_NUMBER() OVER (PARTITION BY s.CustomerKey ORDER BY SUM(s.SalesAmount) DESC) AS rn
        FROM dbo.FactInternetSales s
        JOIN dbo.DimProduct p ON p.ProductKey = s.ProductKey
        LEFT JOIN dbo.DimProductSubcategory ps ON ps.ProductSubcategoryKey = p.ProductSubcategoryKey
        LEFT JOIN dbo.DimProductCategory pc ON pc.ProductCategoryKey = ps.ProductCategoryKey
        GROUP BY s.CustomerKey, COALESCE(pc.EnglishProductCategoryName, 'Uncategorized')
    ) x WHERE rn = 1
), Scored AS (
    SELECT m.*,
           f.ProductCategory AS FavoriteCategory,
           CASE
             WHEN m.RecencyDays > 365 THEN 'At-Risk'
             WHEN m.TotalSpend >= 5000 OR m.OrderCount >= 8 THEN 'VIP'
             ELSE 'Regular'
           END AS Segment,
           CASE
             WHEN m.RecencyDays > 730 THEN 'High'
             WHEN m.RecencyDays > 365 THEN 'Medium'
             ELSE 'Low'
           END AS ChurnRisk
    FROM CustomerMetrics m LEFT JOIN FavoriteCategory f ON f.CustomerKey = m.CustomerKey
)
SELECT TOP (@TopN) CustomerKey, CustomerName, LastPurchaseDate, RecencyDays,
       OrderCount, TotalSpend, FavoriteCategory, Segment, ChurnRisk
FROM Scored
WHERE @CustomerKey = 0 OR CustomerKey = @CustomerKey
ORDER BY CASE ChurnRisk WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END,
         TotalSpend DESC;

