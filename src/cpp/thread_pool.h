#pragma once

#include <vector>
#include <queue>
#include <memory>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <future>
#include <functional>
#include <stdexcept>

namespace concurrent
{
    // Adapted version of
    // https://github.com/progschj/ThreadPool
    class thread_pool
    {
    public:
        thread_pool(size_t size)
            : _stop(false)
        {
            for (size_t i = 0; i < size; ++i)
                _pool.emplace_back(
                    [this]
                    {
                        while (is_alive())
                        {
                            std::function<void()> task;

                            {
                                std::unique_lock<std::mutex> lock(_queue_mutex);
                                _condition.wait(lock,
                                    [this] {
                                        return _stop || !_tasks.empty();
                                    }
                                );

                                if (!is_alive())
                                {
                                    return;
                                }

                                task = std::move(_tasks.front());
                                _tasks.pop();
                            }

                            task();
                        }
                    }
                );
        }

        thread_pool(const thread_pool&) = delete;
        thread_pool(thread_pool&&) = delete;
        thread_pool& operator=(const thread_pool&) = delete;
        thread_pool operator=(thread_pool&&) = delete;

        ~thread_pool()
        {
            {
                std::unique_lock<std::mutex> lock(_queue_mutex);
                _stop = true;
            }

            _condition.notify_all();

            for (std::thread& worker: _pool)
            {
                worker.join();
            }
        }

        template <class Function,
                  class... Args,
                  class return_type = typename std::result_of<Function(Args...)>::type>
        auto submit(Function&& function, Args&&... args)
            -> std::future<return_type>
        {
            auto binded = std::bind(std::forward<Function>(function),
                                    std::forward<Args>(args)...);

            using task_type = std::packaged_task<return_type()>;
            auto task = std::make_shared<task_type>(binded);

            std::future<return_type> future = task->get_future();
            {
                std::unique_lock<std::mutex> lock(_queue_mutex);

                // don't allow enqueueing after stopping the pool
                if (_stop)
                {
                    throw std::runtime_error("enqueue on stopped ThreadPool");
                }

                _tasks.emplace([task]() { (*task)(); });
            }

            _condition.notify_one();
            return future;
        }

    private:
        bool is_alive()
        {
            return !(_stop && _tasks.empty());
        }

    private:
        std::vector<std::thread> _pool;
        std::queue<std::function<void()>> _tasks;

        std::mutex _queue_mutex;
        std::condition_variable _condition;
        bool _stop;
    };

}
