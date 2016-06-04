#include <string>
#include <iostream>
#include <assert.h>
#include <map>
#include <vector>
#include <thread>
#include <chrono>
#include <cstdlib>

#include <cache.h>
#include <thread_pool.h>

struct Foo
{
    int a;
/*
    Foo(int _a)
        : a(_a)
    {}
*/
    //Foo(Foo& other) = delete;
/*
    Foo(Foo&& other)
        : a(std::move(other.a))
    {}
*/
    bool operator==(const Foo& other)
    {
        return a == other.a;
    }
};

using namespace concurrent;

void test_create()
{
    lru_cache<std::string, Foo> x;
    assert(x.empty());
    assert(x.size() == 0);
    assert(x.max_size() == 50);

    lru_cache<std::string, Foo> y(10);
    assert(y.max_size() == 10);
}

void test_simple_insert()
{
    lru_cache<std::string, Foo> x;

    Foo f { 1 };
    auto result = x.insert(std::make_pair("f", f));
    assert(result.second == true);
    assert(result.first->second == f);

    result = x.insert(std::make_pair("f", f));
    assert(result.second == false);
    assert(result.first->second == f);

    Foo g { 10 };
    result = x.insert(std::make_pair("g", g));
    assert(result.second == true);
    assert(result.first->second == g);
}

void test_lru_insert()
{
    const int max_count = 20;
    lru_cache<std::string, Foo> cache(max_count);

    for (size_t i = 0; i < max_count; ++i)
    {
        Foo f { (int)i };
        std::string key = "f";
        key += std::to_string(i);

        auto result = cache.insert(std::make_pair(key, f));
        assert(result.second == true);
        assert(result.first->second == f);
        assert(cache.size() == i + 1);
        assert(cache[key] == f);
    }

    std::map<std::string, Foo> objects;
    for (size_t i = max_count; i < 2 * max_count; ++i)
    {
        Foo f { (int)i };
        std::string key = "f";
        key += std::to_string(i);

        auto result = cache.insert(std::make_pair(key, f));
        assert(result.second == true);
        assert(result.first->second == f);
        assert(cache.size() == max_count);
        assert(cache[key] == f);

        objects[key] = f;
    }

    for (auto kv : objects)
    {
        assert(cache[kv.first] == kv.second);
    }
}

void test_lru_update()
{
    const int max_count = 5;
    lru_cache<std::string, Foo> cache(max_count);

    for (size_t i = 0; i < max_count; ++i)
    {
        auto it = cache.insert(std::make_pair(std::to_string(i),
                                              Foo { (int)i } ));
        assert(it.second == true);
        assert(it.first->second == Foo { (int) i});
    }
    cache["0"];
    cache["1"];
    cache["2"];

    cache.insert(std::make_pair("42",
                                Foo { 42 }));

    std::vector<std::string> keys = { "0", "1", "2", "4", "42" };
    for (auto key: keys)
    {
        (void)cache[key];
    }
    assert(cache.size() == 5);
    assert(cache.max_size() == 5);
}

std::mutex cout_mutex;

void worker_func()
{
    {
        std::lock_guard<std::mutex> lock(cout_mutex);
    	std::cout << "Thread " << std::this_thread::get_id() << std::endl;
    }

    std::this_thread::sleep_for(std::chrono::seconds(1));
}

void test_pool()
{
    const size_t pool_size = 4;
    thread_pool pool(pool_size);

    for (size_t i = 0; i < pool_size; ++i)
    {
        pool.submit(worker_func);
    }
}

Foo foo_calc(std::string string)
{
    return Foo { (int)(rand() % 100) };
}


static std::exception_ptr teptr = nullptr;

template <class Key, class T, typename lru = lru_cache<Key, T>>
auto get_lru_cache_pointer() -> std::shared_ptr<lru>
{
    static std::shared_ptr<lru> instance = std::make_shared<lru>();
    return instance;
}

template <class Key, class T, T(*Function)(Key)>
class lru_cache_wrapper
{
public:
    lru_cache_wrapper(size_t cache_size)
        : _pcache(get_lru_cache_pointer<Key, T>())
    {}

    Foo operator()(const Key& key)
    {
        try
        {
            auto it = _pcache->find(key);
            if (it == _pcache->end())
            {
                T result_obj = std::move(Function(key));
                _pcache->insert(std::make_pair(key, result_obj));
                return std::move(result_obj);
            }
            else
            {
                return it->second;
            }
        }
        catch (std::exception e)
        {
            teptr = std::current_exception();
        }
        return T();
    }

private:
    std::shared_ptr<lru_cache<Key, T>> _pcache;
};


void test_multithreaded_lru()
{
    const size_t pool_size = 10;
    thread_pool pool(pool_size);

    const int cache_size = 10;
    lru_cache_wrapper<std::string, Foo, foo_calc> wrapper(cache_size);

    std::vector<boost::future<Foo>> futures;
    std::vector<std::string> keys = { "1", "2", "3", "4", "5", "6", "7" };
    for (size_t i = 0; i < 10 * keys.size(); ++i)
    {
        futures.emplace_back(
            std::move(pool.submit(
                    wrapper,
                    keys[i % keys.size()]
                )
            )
        );
    }

    try
    {
        boost::wait_for_all(futures.begin(), futures.end());
        if (teptr)
        {
            std::rethrow_exception(teptr);
        }
    } catch (std::exception e) {
        std::cout << e.what() << std::endl;
    }

}

int main()
{
    test_create();
    test_simple_insert();
    test_lru_insert();
    test_lru_update();
    test_pool();
    test_multithreaded_lru();

    std::cout << "OK" << std::endl;
    return 0;
}
