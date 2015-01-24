{%- extends 'basic.tpl' -%}

{% block input_group -%}
{% endblock input_group %}

{% block in_prompt -%}
{%- endblock in_prompt %}

{% block empty_in_prompt -%}
{%- endblock empty_in_prompt %}

{% block input %}
{%- endblock input %}

{% block output %}
{%- if output.output_type == 'pyout' -%}
    <pre>{{ output.text | ansi2html }}</pre>
{%- else -%}
    {{ super() }}
{%- endif -%}
{% endblock output %}
