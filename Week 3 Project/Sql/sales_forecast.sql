/* Read-only seasonal baseline for AdventureWorksDW2022.
   n8n replaces {{ $json.forecast_months }} with a validated integer (1..12). */
DECLARE @ForecastMonths int = {{ Math.min(12, Math.max(1, Number($json.forecast_months || 6))) }};

WITH Sales AS (
    SELECT d.FullDateAlternateKey AS OrderDate,
           'Internet' AS Channel,
           pc.EnglishProductCategoryName AS ProductCategory,
           CAST(s.SalesAmount AS decimal(19,2)) AS Revenue
    FROM dbo.FactInternetSales s
    JOIN dbo.DimDate d ON d.DateKey = s.OrderDateKey
    JOIN dbo.DimProduct p ON p.ProductKey = s.ProductKey
    LEFT JOIN dbo.DimProductSubcategory ps ON ps.ProductSubcategoryKey = p.ProductSubcategoryKey
    LEFT JOIN dbo.DimProductCategory pc ON pc.ProductCategoryKey = ps.ProductCategoryKey
    UNION ALL
    SELECT d.FullDateAlternateKey,
           'Reseller',
           pc.EnglishProductCategoryName,
           CAST(s.SalesAmount AS decimal(19,2))
    FROM dbo.FactResellerSales s
    JOIN dbo.DimDate d ON d.DateKey = s.OrderDateKey
    JOIN dbo.DimProduct p ON p.ProductKey = s.ProductKey
    LEFT JOIN dbo.DimProductSubcategory ps ON ps.ProductSubcategoryKey = p.ProductSubcategoryKey
    LEFT JOIN dbo.DimProductCategory pc ON pc.ProductCategoryKey = ps.ProductCategoryKey
), Monthly AS (
    SELECT DATEFROMPARTS(YEAR(OrderDate), MONTH(OrderDate), 1) AS MonthStart,
           Channel, COALESCE(ProductCategory, 'Uncategorized') AS ProductCategory,
           SUM(Revenue) AS Revenue
    FROM Sales
    GROUP BY DATEFROMPARTS(YEAR(OrderDate), MONTH(OrderDate), 1), Channel,
             COALESCE(ProductCategory, 'Uncategorized')
), Bounds AS (
    SELECT MAX(MonthStart) AS LastActualMonth FROM Monthly
), N AS (
    SELECT 1 AS n UNION ALL SELECT n + 1 FROM N WHERE n < 12
), FutureMonths AS (
    SELECT DATEADD(month, n, b.LastActualMonth) AS ForecastMonth
    FROM Bounds b CROSS JOIN N WHERE n <= @ForecastMonths
), Series AS (
    SELECT DISTINCT Channel, ProductCategory FROM Monthly
), Forecast AS (
    SELECT f.ForecastMonth, s.Channel, s.ProductCategory,
           COALESCE(seasonal.SeasonalAverage, trailing.TrailingAverage) AS ForecastRevenue,
           CASE WHEN seasonal.SeasonalAverage IS NOT NULL
                THEN 'same-month seasonal average' ELSE 'trailing-12-month average' END AS Method,
           COALESCE(seasonal.ObservationCount, trailing.ObservationCount) AS ObservationCount
    FROM FutureMonths f CROSS JOIN Series s CROSS JOIN Bounds b
    OUTER APPLY (
        SELECT AVG(m.Revenue) SeasonalAverage, COUNT(*) ObservationCount
        FROM Monthly m
        WHERE m.Channel = s.Channel AND m.ProductCategory = s.ProductCategory
          AND MONTH(m.MonthStart) = MONTH(f.ForecastMonth)
          AND m.MonthStart <= b.LastActualMonth
    ) seasonal
    OUTER APPLY (
        SELECT AVG(m.Revenue) TrailingAverage, COUNT(*) ObservationCount
        FROM Monthly m
        WHERE m.Channel = s.Channel AND m.ProductCategory = s.ProductCategory
          AND m.MonthStart > DATEADD(month, -12, b.LastActualMonth)
          AND m.MonthStart <= b.LastActualMonth
    ) trailing
)
SELECT CONVERT(char(7), ForecastMonth, 120) AS ForecastMonth,
       Channel, ProductCategory,
       CAST(ForecastRevenue AS decimal(19,2)) AS ForecastRevenue,
       Method, ObservationCount
FROM Forecast
ORDER BY ForecastMonth, Channel, ProductCategory
OPTION (MAXRECURSION 12);

