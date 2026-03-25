import Cocoa

guard CommandLine.arguments.count > 1,
      let pid = pid_t(CommandLine.arguments[1]) else {
    exit(1)
}

let targetPID = pid

// Record initial mouse position
let initialPos = NSEvent.mouseLocation

// Poll mouse position — any movement kills audio
let timer = Timer.scheduledTimer(withTimeInterval: 0.1, repeats: true) { _ in
    let pos = NSEvent.mouseLocation
    let dx = abs(pos.x - initialPos.x)
    let dy = abs(pos.y - initialPos.y)
    if dx > 5 || dy > 5 {
        kill(targetPID, SIGTERM)
        exit(0)
    }
}

// Auto-exit after 60 seconds
DispatchQueue.main.asyncAfter(deadline: .now() + 60) {
    exit(0)
}

RunLoop.current.run()
