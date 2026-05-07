using CSharpServiceDemo.Models;

var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();

var items = new List<MarketplaceItem>
{
    new(1, "Starter Skin Pack", "cosmetic", 4.99m),
    new(2, "Adventure Map", "content", 9.99m),
    new(3, "Creator Bundle", "bundle", 14.99m)
};

app.MapGet("/health", () => Results.Ok(new { status = "ok" }));
app.MapGet("/items", () => Results.Ok(items));

app.MapGet("/items/{id:int}", (int id) =>
{
    var item = items.FirstOrDefault(i => i.Id == id);
    return item is null
        ? Results.NotFound(new { error = "item_not_found" })
        : Results.Ok(item);
});

app.Run();
