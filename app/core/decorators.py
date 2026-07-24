import functools
import inspect
import json
from typing import Callable, Optional, List

from pydantic import BaseModel
from app.database.cache import cache_client


def cached_operation(ttl, cache_prefix: str = "default", cache_key_params: Optional[List[str]] = None, expected_model: Optional[BaseModel] = None):
    def decorator(func: Callable) -> Callable:
        sig:inspect.Signature = inspect.signature(func)
        param_names = sig.parameters.keys()
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                bound = sig.bind(*args, **kwargs)
                bound.apply_defaults()
                params = bound.arguments
            except Exception as e:
                raise ValueError(f"Error binding parameters for function {func.__name__}: {e}")
            
            params = {k: v for k,v in params.items() if k not in ['self', 'cls']}

            if cache_key_params:
                key_values = [str(params.get(param, '')) for param in cache_key_params]
            else:
                key_values = [str(params.get(param, '')) for param in param_names if param not in ['self', 'cls']]
            
            cache_key = f"{cache_prefix}:" + ":".join(key_values)

            try:
                cached_result = cache_client.get_cache(key=cache_key)
                if cached_result is not None:
                    if expected_model:
                        return _deserialize(cached_result, expected_model)
                    return cached_result
            except Exception as e:
                print(f"Error retrieving cache for key {cache_key}: {e}")

            result = func(*args, **kwargs) 

            cache_client.set_cache(key=cache_key, value=_serialize(result), ttl=ttl)
            
            return result

        return wrapper

    return decorator

def _serialize(result):
    if isinstance(result, BaseModel):
        return result.model_dump_json()
    if isinstance(result, List[BaseModel]):
        return json.dumps([part.model_dump_json() for part in result])
    if isinstance(result, (dict, list)):
        return json.dumps(result)
    return result

def _deserialize(result, expected_model):
    if expected_model:
        if issubclass(expected_model, BaseModel):
            return expected_model.model_validate_json(result)
        if isinstance(result, list) and all(isinstance(item, dict) for item in result):
            return [expected_model.model_validate_json(json.dumps(item)) for item in result]
    return result