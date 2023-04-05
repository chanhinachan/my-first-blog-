from django import template

register = template.Library() # Djangoのテンプレートタグライブラリ

# カスタムフィルタとして登録する
@register.simple_tag
def get_count(count, pk):
    return count[pk]