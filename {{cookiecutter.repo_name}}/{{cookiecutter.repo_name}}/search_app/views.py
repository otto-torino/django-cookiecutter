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
    
    # Use a defaultdict to group results
    grouped_results = defaultdict(list)
    total_results_count = 0

    context = {
        'query': query_text,
        'grouped_results': {},
        'total_results_count': 0,
    }

    if query_text:
        search_query = SearchQuery(query_text, search_type='websearch')
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
            search_vector = SearchVector(*search_fields)

            headline_annotations = {
                f'headline_{field}': SearchHeadline(field, search_query, **headline_options)
                for field in search_fields
            }

            queryset = model.objects.annotate(
                search=search_vector,
                rank=SearchRank(search_vector, search_query),
                **headline_annotations
            ).filter(search=search_query)
            
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
