from src.agent import CodingAgent


def main():
    agent = CodingAgent()

    print("Autonomous Coding Agent - V7")
    print("Type 'exit' to quit.\n")

    while True:

        task = input("Task: ")

        if task.lower() in {
            "exit",
            "quit",
        }:
            break

        try:
            result = agent.run(task)

            print("\nAgent:")
            print(result)

            if agent.last_metrics is not None:

                print(
                    agent.last_metrics.format_report(
                        trace_path=(
                            agent.last_trace_path
                        )
                    )
                )

        except Exception as error:

            print(
                f"\nError: {error}\n"
            )

            # Even failed runs may have useful metrics.
            if agent.last_metrics is not None:

                print(
                    agent.last_metrics.format_report(
                        trace_path=(
                            agent.last_trace_path
                        )
                    )
                )


if __name__ == "__main__":
    main()