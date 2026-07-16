from django.shortcuts import render
from django.contrib.postgres.search import (
    SearchVector, 
    SearchQuery, 
    SearchRank, 
    SearchHeadline
)
from django.apps import apps
from .models import Searchable
from collections import defaultdict
from django.utils.translation import get_language
from django.conf import settings

def search_view(request):
    """
    Handles the search logic.
    - Finds all models that inherit from the `Searchable` abstract model.
    - Performs a full-text search across the specified fields of these models.
    - Dynamically generates a headline snippet from the specific field where
      the search term was found.
    - Aggregates and groups the results by model, then ranks them.
    """
    query_text = request.GET.get('q', '').strip()
    grouped_results = defaultdict(list)
    total_results_count = 0
    current_language = get_language()
    LANG_TO_PG_CONFIG = dict(settings.LANGUAGES)
    pg_search_config = LANG_TO_PG_CONFIG.get(current_language, 'simple')

    context = {
        'query': query_text,
        'grouped_results': {},
        'total_results_count': 0,
    }

    if query_text:
        search_query = SearchQuery(query_text, config=pg_search_config, search_type='websearch')
        all_models = apps.get_models()
        
        searchable_models = [
            model for model in all_models 
            if issubclass(model, Searchable) and not model._meta.abstract
        ]

        highlight_start_tag = '<span class="bg-yellow-200 font-bold">'
        headline_options = {
            'start_sel': highlight_start_tag,
            'stop_sel': '</span>',
            'max_fragments': 3,
            'fragment_delimiter': ' ... '
        }

        for model in searchable_models:
            search_fields = model.get_search_fields()
            search_vector = SearchVector(*search_fields, config=pg_search_config)

            headline_annotations = {
                f'headline_{field}': SearchHeadline(field, search_query, config=pg_search_config, **headline_options)
                for field in search_fields
            }

            queryset = model.get_search_queryset(request).annotate(
                search=search_vector,
                rank=SearchRank(search_vector, search_query),
                **headline_annotations
            ).filter(search=search_query).order_by('id', '-rank').distinct('id')
            
            if queryset.exists():
                model_verbose_name_plural = model._meta.verbose_name_plural.title()
                for item in queryset:
                    best_headline = ''
                    for field in search_fields:
                        headline_content = getattr(item, f'headline_{field}')
                        if headline_content and highlight_start_tag in headline_content:
                            best_headline = headline_content
                            break

                    if not best_headline:
                        for field in search_fields:
                            fallback_content = getattr(item, f'headline_{field}')
                            if fallback_content:
                                best_headline = fallback_content
                                break

                    item.headline = best_headline
                    
                    # Append to the list for that model
                    grouped_results[model_verbose_name_plural].append(item)

        # Sort results within each group by rank and calculate total
        for model_name, results_list in grouped_results.items():
            results_list.sort(key=lambda r: r.rank, reverse=True)
            total_results_count += len(results_list)
            

        # Convert defaultdict to a regular dict for the template
        context['grouped_results'] = dict(grouped_results)
        context['total_results_count'] = total_results_count

    return render(request, 'search_app/search_results.html', context)
