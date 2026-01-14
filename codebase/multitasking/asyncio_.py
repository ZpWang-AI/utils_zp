def run_multitasks(tasks):
    import asyncio
    
    async def async_func(func, args, kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)
    
    async def main():
        async_tasks = [
            async_func(func, args, kwargs)
            for func, args, kwargs in tasks
        ]
        results = await asyncio.gather(*async_tasks)  
        return results
    
    return asyncio.run(main())
