# Boards

_Command Boards_ are a quick way to create custom command launchers.

## Templating

The `template` of board will be rendered with the [`nunjucks`][nunjucks] templating
syntax, which is _mostly_ compatible with [jinja2][jinja2].

[nunjucks]: https://mozilla.github.io/nunjucks/templating.html
[jinja2]: https://jinja.palletsprojects.com/en/3.1.x/templates/

### Rendering Context

When rendering, the variable `app` is a description of the current application, with
some useful information:

## Cookbook

```{hint}
Here are some useful starting points for command boards. These can be pasted into the
_Advanced Settings &raquo; Command Boards &raquo; boards_ section.
```

### Show all commands as buttons

```html
{% for id, command in app.commands.items() | sort %}
<button data-command-id="{{ id }}" title="{{ command.label }}">{{ id }}</button>
{% endfor %}
```
