from tui import OctopusApp, TentacleManager

def main():
    tentacle_manager = TentacleManager()
    app = OctopusApp(tentacle_manager=tentacle_manager)
    app.run()

if __name__ == "__main__":
    main()
