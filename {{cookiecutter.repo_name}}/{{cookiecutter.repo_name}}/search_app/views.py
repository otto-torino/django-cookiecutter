from django.shortcuts import render
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.apps import apps
from .models import Searchable

def search_view(request):
    """
    Handles the search logic.
    - Finds all models that inherit from the `Searchable` abstract model.
    - Performs a full-text search across the specified fields of these models.
    - Aggregates and ranks the results.
    """
    query_text = request.GET.get('q', '').strip()
    search_results = []
    
    # Context to be passed to the template
    context = {
        'query': query_text,
        'results': [],
    }

    if query_text:
        # Create a SearchQuery object. Using 'websearch' config is good for parsing
        # queries like "cat & dog" or "cat | dog"
        search_query = SearchQuery(query_text, search_type='websearch')

        # Get all models registered in the project
        all_models = apps.get_models()
        
        # Filter for models that are subclasses of our Searchable model
        searchable_models = [
            model for model in all_models 
            if issubclass(model, Searchable) and not model._meta.abstract
        ]

        for model in searchable_models:
            # For each model, define the search vector using its specified fields
            search_fields = model.get_search_fields()
            search_vector = SearchVector(*search_fields)

            # Query the model:
            # 1. Annotate with the search vector.
            # 2. Annotate with the rank of the result.
            # 3. Filter based on the search query.
            # 4. Order by the rank in descending order.
            queryset = model.objects.annotate(
                search=search_vector,
                rank=SearchRank(search_vector, search_query)
            ).filter(search=search_query).order_by('-rank')
            
            # Add the results to our combined list
            search_results.extend(list(queryset))

        # Sort all combined results by rank, highest first.
        # The database already ordered each queryset by rank, but this ensures
        # that results from different models are correctly interleaved.
        sorted_results = sorted(search_results, key=lambda r: r.rank, reverse=True)
        
        context['results'] = sorted_results

    return render(request, 'search_app/search_results.html', context)
