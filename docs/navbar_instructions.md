
# Integration Instructions for Navigation Menu

Insert the following line immediately after the `<body>` tag in each HTML template:

```html
{% include 'navbar.html' %}
```

This assumes `navbar.html` is located in your `templates/` directory.

### Pages Updated by Default

- `Status` → `/`
- `Upload` → `/upload`
- `Admin` → `/admin`

You can expand this layout by adding more `<li>` items to the `<ul class="navbar-nav">` in `navbar.html`.

Make sure Flask is configured to find the template and that `render_template()` is used properly in the routes.
