#!/usr/bin/env python3

# Monkey patch to debug middleware issues
import starlette.middleware
import starlette.applications

original_build_middleware_stack = starlette.applications.Starlette.build_middleware_stack

def debug_build_middleware_stack(self):
    print(f"DEBUG: Building middleware stack, middleware count: {len(self.user_middleware)}")
    for i, middleware in enumerate(self.user_middleware):
        print(f"  Middleware {i}: {middleware} (type: {type(middleware)})")
        if hasattr(middleware, '__iter__') and not isinstance(middleware, str):
            try:
                items = list(middleware)
                print(f"    As list: {items} (length: {len(items)})")
            except:
                print(f"    Could not convert to list")
    
    # Now call original method and see what fails
    try:
        result = original_build_middleware_stack(self)
        print("DEBUG: Middleware stack built successfully")
        return result
    except Exception as e:
        print(f"DEBUG: Error in build_middleware_stack: {e}")
        
        # Try to identify the problematic middleware
        middleware = self.user_middleware
        print(f"DEBUG: Raw middleware list: {middleware}")
        for i, mw_item in enumerate(reversed(middleware)):
            print(f"DEBUG: Reversed item {i}: {mw_item}")
            try:
                cls, options = mw_item
                print(f"  Unpacked OK: cls={cls}, options={options}")
            except Exception as unpack_error:
                print(f"  Unpacking FAILED: {unpack_error}")
        raise

# Monkey patch the method
starlette.applications.Starlette.build_middleware_stack = debug_build_middleware_stack

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=500)

@app.get("/test")
async def test():
    return {"status": "ok"}

print("About to test middleware stack build...")
try:
    # This should trigger the middleware stack building
    from starlette.testclient import TestClient
    client = TestClient(app)
    response = client.get("/test")
    print(f"Response: {response.status_code}, {response.json()}")
except Exception as e:
    print(f"Test failed: {e}")
    import traceback
    traceback.print_exc()