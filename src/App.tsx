import { useState, useEffect, useRef } from "react";
import { 
  Terminal, ShieldCheck, Settings, AlertTriangle, Play, HelpCircle, 
  Copy, Check, RefreshCw, Cpu, Database, Bell, Globe, Sparkles, AlertCircle
} from "lucide-react";
import { motion, AnimatePresence } from "motion/react";

// Types
interface LogLine {
  timestamp: string;
  text: string;
  type: "info" | "success" | "warning" | "error" | "debug";
}

export default function App() {
  // Custom specifications that can be edited to generate code
  const [targetUrl, setTargetUrl] = useState("https://in.bookmyshow.com/cinemas/coimbatore/cosmo-cinemas-peelamedu-ac-4k-rgb-lasecoimbatore/buytickets/CCCB/20260720");
  const [cinemaName, setCinemaName] = useState("Cosmo Cinemas Peelamedu");
  const [showDate, setShowDate] = useState("20 July 2026");

  // Simulated state for live dashboard
  const [isSimulating, setIsSimulating] = useState(false);
  const [simulationStep, setSimulationStep] = useState(0);
  const [simUptime, setSimUptime] = useState(0);
  const [simQueries, setSimQueries] = useState(14);
  const [simBackoffs, setSimBackoffs] = useState(2);
  const [simErrors, setSimErrors] = useState(0);
  const [simLatency, setSimLatency] = useState(380);
  const [simStrategy, setSimStrategy] = useState("Requests");
  const [simConfidence, setSimConfidence] = useState(0);
  const [simStatus, setSimStatus] = useState("CLOSED");
  const [simHash, setSimHash] = useState("7f8a9c2b");
  const [simChanges, setSimChanges] = useState(false);
  const [alertSent, setAlertSent] = useState(false);
  const [isLiveOpen, setIsLiveOpen] = useState(false);
  const [simLog, setSimLog] = useState<LogLine[]>([
    { timestamp: "11:42:01", text: "Booting BookMyShow AI Monitor Engine...", type: "info" },
    { timestamp: "11:42:02", text: "Cached hash target: 7f8a9c2b", type: "info" },
    { timestamp: "11:42:02", text: "System self-test completed successfully.", type: "success" }
  ]);
  const [latencies, setLatencies] = useState<number[]>([320, 340, 310, 420, 380, 410, 390, 350, 400, 380]);

  // Terminal scroll handler
  const terminalEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (terminalEndRef.current) {
      terminalEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [simLog]);

  // Uptime ticker
  useEffect(() => {
    const interval = setInterval(() => {
      setSimUptime((prev) => prev + 1);
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  const addSimLog = (text: string, type: "info" | "success" | "warning" | "error" | "debug" = "info") => {
    const now = new Date();
    const timestamp = now.toTimeString().split(" ")[0];
    setSimLog((prev) => [...prev, { timestamp, text, type }]);
  };

  // Run simulated audit
  const runSimulation = () => {
    if (isSimulating) return;
    setIsSimulating(true);
    setSimulationStep(1);
    setSimStrategy("Requests");
    setSimConfidence(0);
    setSimStatus("CLOSED");
    setSimChanges(false);
    
    addSimLog("Initializing on-demand live security audit...", "info");
    
    setTimeout(() => {
      // Step 2: Requests Phase
      setSimulationStep(2);
      setSimQueries((q) => q + 1);
      setSimLatency(randomLatency(250, 450));
      addSimLog(`Initiating Requests call [Attempt 1/3] to ticket endpoint...`, "info");
      
      setTimeout(() => {
        // Step 3: Cloudflare Block Simulation
        setSimulationStep(3);
        setSimErrors((e) => e + 1);
        addSimLog("Warning: Blocked by Cloudflare (HTTP 403 Challenge detected)", "warning");
        addSimLog("Requests vector blocked. Gracefully launching browser fallback...", "info");
        
        setTimeout(() => {
          // Step 4: Playwright Launch
          setSimulationStep(4);
          setSimStrategy("Playwright");
          addSimLog("Launching headless Chromium browser session...", "info");
          
          setTimeout(() => {
            // Step 5: Rendering & Content retrieval
            setSimulationStep(5);
            setSimQueries((q) => q + 1);
            const lat = randomLatency(1200, 1850);
            setSimLatency(lat);
            setLatencies((prev) => [...prev.slice(1), lat]);
            addSimLog("Headless browser loaded. DOM content successfully fetched.", "success");
            
            setTimeout(() => {
              // Step 6: Confidence evaluation
              setSimulationStep(6);
              // Calculate randomized decision for showcase (let's do 50% chance bookings are live)
              const bookingLive = Math.random() > 0.45;
              
              if (bookingLive) {
                setSimConfidence(95);
                setSimStatus("ACTIVE");
                setSimChanges(true);
                const nextHash = "5e2b8d1a";
                setSimHash(nextHash);
                
                addSimLog("Confidence Engine: Found active ticketing offers (+35%)", "success");
                addSimLog("Confidence Engine: Extracted 3 active seatlayout links (+50%)", "success");
                addSimLog("Confidence Engine: Identified standard showtime schedules (+15%)", "success");
                addSimLog(`Alert: Ticket bookings identified as ACTIVE (95% confidence)`, "success");
                
                setTimeout(() => {
                  setAlertSent(true);
                  addSimLog("Dispatching instant Telegram notification to operator...", "info");
                  addSimLog("Telegram Alert transmitted successfully!", "success");
                  setIsSimulating(false);
                  setSimulationStep(0);
                  setIsLiveOpen(true);
                }, 1000);
              } else {
                setSimConfidence(15);
                setSimStatus("CLOSED");
                setSimChanges(false);
                addSimLog("Confidence Engine: Matched time patterns but found phrase 'Coming Soon' (-40%)", "warning");
                addSimLog("Confidence Engine: No active ticketing offers or seatlayouts present", "info");
                addSimLog("Audit complete. Ticket sales remain CLOSED. No notifications required.", "info");
                setIsSimulating(false);
                setSimulationStep(0);
              }
            }, 1200);
          }, 1200);
        }, 1200);
      }, 1000);
    }, 1000);
  };

  const randomLatency = (min: number, max: number) => {
    return Math.floor(Math.random() * (max - min + 1) + min);
  };



  return (
    <div id="app_root" className="min-h-screen bg-[#050505] text-slate-300 font-mono flex flex-col selection:bg-blue-500/20 selection:text-blue-300">
      
      {/* HEADER BAR */}
      <header className="border-b border-[#1a1a1e] bg-[#0d0d0f]/90 backdrop-blur sticky top-0 z-40 px-4 py-2.5 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="p-1.5 bg-blue-950/20 border border-blue-500/20 rounded text-blue-400">
            <Cpu className="w-4 h-4 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="font-bold text-sm tracking-wider uppercase text-slate-100">BMS TARGET MONITOR</h1>
              <span className="flex items-center gap-1 text-[9px] bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 px-1.5 py-0.5 rounded font-bold tracking-wider uppercase">
                <span className="w-1 h-1 rounded-full bg-emerald-500 shadow-[0_0_8px_#10b981]"></span>
                LIVE
              </span>
            </div>
            <p className="text-[9px] text-slate-500 tracking-wider">SERVERLESS SENTINEL SYSTEM v1.0.0</p>
          </div>
        </div>

      </header>

      {/* COMPANION MAIN WRAPPER */}
      <main className="flex-1 overflow-auto p-4 max-w-7xl mx-auto w-full space-y-4">
        
        {/* DASHBOARD CONTENT */}
        <div className="space-y-4">
            
            {/* INSTRUCTIONAL ACCORDION */}
            <div className="bg-[#0d0d0f] border border-[#1a1a1e] p-4 flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-inner">
              <div className="space-y-1.5">
                <div className="flex items-center space-x-2 text-blue-400">
                  <Sparkles className="w-3.5 h-3.5" />
                  <span className="text-[10px] font-bold tracking-widest uppercase">Interactive Demonstration Simulator</span>
                </div>
                <h2 className="text-sm font-bold text-slate-200">BMS Monitor Simulated Visualizer</h2>
                <p className="text-[11px] text-slate-400 max-w-3xl leading-relaxed">
                  This interface provides an accurate visual representation of the Rich dashboard running inside your GitHub Action. Run a simulated on-demand audit cycle to watch requests fallback to Playwright, evaluate confidence scores, and preview the live alerts.
                </p>
              </div>
              <button
                onClick={runSimulation}
                disabled={isSimulating}
                className="flex items-center justify-center space-x-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-bold tracking-wider uppercase rounded shadow transition duration-200 border border-blue-500 cursor-pointer"
              >
                {isSimulating ? (
                  <>
                    <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                    <span>SIMULATING SCAN...</span>
                  </>
                ) : (
                  <>
                    <Play className="w-3.5 h-3.5" />
                    <span>START AUDIT SCAN</span>
                  </>
                )}
              </button>
            </div>

            {/* LIVE SIMULATOR GRID */}
            <div className="grid grid-cols-1 lg:grid-cols-10 gap-4">
              
              {/* SYSTEM PANEL */}
              <div className="lg:col-span-4 space-y-4">
                
                {/* specs card */}
                <div className="bg-[#0d0d0f] border border-[#1a1a1e] p-3.5 space-y-3 shadow-inner">
                  <div className="border-b border-[#1a1a1e] pb-2 flex items-center justify-between">
                    <span className="text-[10px] font-bold tracking-widest text-blue-400 uppercase flex items-center gap-1.5">
                      <span>📡 MONITOR SPECIFICATION</span>
                    </span>
                    <Settings className="w-3.5 h-3.5 text-slate-500" />
                  </div>
                  <div className="space-y-2 text-[11px]">
                    <div className="flex justify-between items-center border-b border-slate-900/40 pb-1">
                      <span className="text-slate-500">Target Venue:</span>
                      <span className="text-slate-200 font-bold">{cinemaName}</span>
                    </div>
                    <div className="flex justify-between items-center border-b border-slate-900/40 pb-1">
                      <span className="text-slate-500">Target Date:</span>
                      <span className="text-amber-400 font-bold">{showDate}</span>
                    </div>
                    <div className="flex flex-col space-y-1">
                      <span className="text-slate-500">Endpoint URL:</span>
                      <span className="text-[9px] text-slate-400 bg-[#09090b] border border-[#1a1a1e] p-1.5 rounded break-all select-all leading-normal">
                        {targetUrl}
                      </span>
                    </div>
                  </div>
                </div>

                {/* system metrics */}
                <div className="bg-[#0d0d0f] border border-[#1a1a1e] p-3.5 space-y-3 shadow-inner">
                  <div className="border-b border-[#1a1a1e] pb-2 flex items-center justify-between">
                    <span className="text-[10px] font-bold tracking-widest text-blue-400 uppercase flex items-center gap-1.5">
                      <span>🔋 SYSTEM METRICS</span>
                    </span>
                    <Cpu className="w-3.5 h-3.5 text-blue-500" />
                  </div>
                  <div className="space-y-2 text-[11px]">
                    <div className="flex justify-between items-center border-b border-slate-900/40 pb-1">
                      <span className="text-slate-500">Uptime Tracker:</span>
                      <span className="text-slate-200 font-bold">{simUptime}s</span>
                    </div>
                    <div className="flex justify-between items-center border-b border-slate-900/40 pb-1">
                      <span className="text-slate-500">System Memory:</span>
                      <span className="text-slate-200 font-bold">14.65 MB</span>
                    </div>
                    <div className="flex justify-between items-center border-b border-slate-900/40 pb-1">
                      <span className="text-slate-500">Scraping Invocations:</span>
                      <span className="text-slate-200 font-bold">{simQueries}</span>
                    </div>
                    <div className="flex justify-between items-center border-b border-slate-900/40 pb-1">
                      <span className="text-slate-500">Backoffs / Retries:</span>
                      <span className="text-slate-200 font-bold">{simBackoffs}</span>
                    </div>
                    <div className="flex justify-between items-center border-b border-slate-900/40 pb-1">
                      <span className="text-slate-500">Failed Requests:</span>
                      <span className={`font-bold ${simErrors > 0 ? "text-red-400" : "text-slate-200"}`}>{simErrors}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-slate-500">Telegram Gateway:</span>
                      <span className={`flex items-center gap-1 font-bold ${alertSent ? "text-emerald-400" : "text-slate-500"}`}>
                        {alertSent ? (
                          <>
                            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-ping"></span>
                            ACTIVE (1 Sent)
                          </>
                        ) : "● READY"}
                      </span>
                    </div>
                  </div>
                </div>

              </div>

              {/* LIVE SCRAPE ENGINE TERMINAL */}
              <div className="lg:col-span-6 flex flex-col bg-[#0d0d0f] border border-[#1a1a1e] rounded overflow-hidden min-h-[400px] shadow-inner">
                
                {/* TERMINAL HEADER */}
                <div className="bg-[#09090b] px-3.5 py-2 border-b border-[#1a1a1e] flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 rounded-full bg-red-500/60 border border-red-500/20"></div>
                      <div className="w-2 h-2 rounded-full bg-yellow-500/60 border border-yellow-500/20"></div>
                      <div className="w-2 h-2 rounded-full bg-green-500/60 border border-green-500/20"></div>
                    </div>
                    <span className="text-[10px] font-bold text-slate-400 ml-1.5 uppercase tracking-wider">LIVE AUDIT ENGINE</span>
                  </div>
                  <div className="flex items-center space-x-2 text-[10px]">
                    <span className="text-slate-500">Strategy:</span>
                    <span className={`px-1.5 py-0.5 rounded text-[9px] font-bold border ${
                      simStrategy === "Requests" ? "bg-blue-950/40 text-blue-400 border-blue-500/20" : "bg-purple-950/40 text-purple-400 border-purple-500/20"
                    }`}>
                      {simStrategy.toUpperCase()}
                    </span>
                  </div>
                </div>

                {/* TERMINAL CONTENT */}
                <div className="flex-1 p-3 font-mono text-[11px] overflow-y-auto space-y-1 bg-[#09090b] min-h-[250px] max-h-[320px] leading-relaxed select-text">
                  {simLog.map((log, index) => (
                    <div key={index} className="flex space-x-2 items-start">
                      <span className="text-slate-600 text-[10px] select-none">[{log.timestamp}]</span>
                      <span className={`flex-grow ${
                        log.type === "success" ? "text-emerald-400" :
                        log.type === "warning" ? "text-amber-400" :
                        log.type === "error" ? "text-red-400 font-bold" :
                        log.type === "debug" ? "text-blue-400" : "text-slate-300"
                      }`}>
                        {log.text}
                      </span>
                    </div>
                  ))}
                  {isSimulating && (
                    <div className="flex items-center space-x-2 text-blue-400 animate-pulse mt-1">
                      <RefreshCw className="w-3 h-3 animate-spin" />
                      <span className="text-[10px]">Processing execution pipeline step {simulationStep}...</span>
                    </div>
                  )}
                  <div ref={terminalEndRef} />
                </div>

                {/* TERMINAL METRICS PANEL */}
                <div className="border-t border-[#1a1a1e] bg-[#0d0d0f]/60 p-3 grid grid-cols-2 md:grid-cols-4 gap-3">
                  <div className="space-y-1">
                    <span className="text-slate-500 text-[9px] font-bold uppercase tracking-wider block">LATENCY RESPONSE</span>
                    <span className="text-slate-200 text-xs font-bold">{simLatency} ms</span>
                  </div>
                  <div className="space-y-1">
                    <span className="text-slate-500 text-[9px] font-bold uppercase tracking-wider block">CONFIDENCE METRIC</span>
                    <span className={`text-xs font-bold ${simConfidence > 50 ? "text-emerald-400 shadow-[0_0_8px_rgba(16,185,129,0.15)]" : "text-slate-300"}`}>
                      {simConfidence}%
                    </span>
                  </div>
                  <div className="space-y-1">
                    <span className="text-slate-500 text-[9px] font-bold uppercase tracking-wider block">SIGNATURE HASH</span>
                    <span className="text-slate-200 text-xs font-bold truncate block">{simHash}</span>
                  </div>
                  <div className="space-y-1">
                    <span className="text-slate-500 text-[9px] font-bold uppercase tracking-wider block">BOOKING FLAG</span>
                    <span className={`text-xs font-bold ${simStatus === "ACTIVE" ? "text-emerald-400" : "text-slate-400"}`}>
                      {simStatus}
                    </span>
                  </div>
                </div>

              </div>

            </div>

            {/* LIVE HISTORICAL LATENCY GRAPH */}
            <div className="bg-[#0d0d0f] border border-[#1a1a1e] p-3.5 space-y-3 shadow-inner">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-bold tracking-widest text-blue-400 uppercase flex items-center gap-1.5">
                  <span>📈 Latency Trend Graph</span>
                </span>
                <span className="text-[10px] text-slate-500">
                  Avg: {Math.round(latencies.reduce((a,b)=>a+b, 0)/latencies.length)}ms
                </span>
              </div>
              <div className="h-14 flex items-end space-x-1 pt-2 border-b border-[#1a1a1e] pb-1">
                {latencies.map((val, idx) => {
                  const maxLat = Math.max(...latencies);
                  const minLat = Math.min(...latencies);
                  const heightPercent = maxLat === minLat ? 50 : ((val - minLat) / (maxLat - minLat)) * 70 + 30;
                  return (
                    <div key={idx} className="flex-1 flex flex-col items-center group relative">
                      <div 
                        className="w-full bg-cyan-500/10 hover:bg-cyan-500/35 border-t border-cyan-400 rounded-t transition-all duration-300"
                        style={{ height: `${heightPercent}%` }}
                      ></div>
                      <span className="absolute -top-7 text-[9px] bg-[#09090b] text-cyan-400 border border-cyan-500/20 px-1 py-0.5 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-10 font-mono">
                        {val}ms
                      </span>
                    </div>
                  );
                })}
              </div>
              <div className="flex justify-between text-[9px] text-slate-500 tracking-wider">
                <span>RUN -10</span>
                <span>RUN -5</span>
                <span>ACTIVE RUN</span>
              </div>
            </div>

          </div>

      </main>

      {/* FOOTER */}
      <footer className="border-t border-[#1a1a1e] bg-[#050505] py-3 px-4 flex flex-col sm:flex-row items-center justify-between gap-2 text-[10px] text-slate-500 font-mono mt-4">
        <span>© NIRANJAN U - 2026</span>
      </footer>

      {/* OVERLAY TICKET DETECTED MODAL */}
      <AnimatePresence>
        {isLiveOpen && (
          <div className="fixed inset-0 bg-black/95 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <motion.div 
              initial={{ opacity: 0, scale: 0.95, y: 15 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 15 }}
              className="bg-[#0d0d0f] border border-emerald-500 p-5 max-w-md w-full space-y-4 relative overflow-hidden shadow-2xl"
            >
              <div className="absolute inset-0 bg-emerald-500/5 pointer-events-none"></div>
              
              <button 
                onClick={() => setIsLiveOpen(false)}
                className="absolute top-3.5 right-3.5 text-slate-500 hover:text-slate-200 font-bold text-[10px] font-mono cursor-pointer px-1.5 py-0.5 border border-[#1a1a1e] hover:border-slate-700 rounded bg-[#09090b]"
              >
                CLOSE [X]
              </button>

              <div className="text-center space-y-2">
                <div className="inline-block p-2 bg-emerald-500/10 border border-emerald-500/25 text-emerald-400 rounded mb-1">
                  <Bell className="w-6 h-6 animate-bounce" />
                </div>
                <h2 className="text-lg font-black text-emerald-400 font-mono uppercase tracking-widest">🎉 BOOKINGS ARE LIVE!</h2>
                <p className="text-[10px] text-slate-400 font-mono tracking-wider">THE SECURITY WATCHDOG DETECTED TICKET RELEASES</p>
              </div>

              <div className="border border-slate-800 bg-[#09090b] p-3.5 space-y-2.5 font-mono text-xs shadow-inner">
                <div className="flex justify-between border-b border-slate-900 pb-2">
                  <span className="text-slate-500 text-[10px] uppercase font-bold">Cinema Venue:</span>
                  <span className="text-slate-200 font-bold text-xs">{cinemaName}</span>
                </div>
                <div className="flex justify-between border-b border-slate-900 pb-2">
                  <span className="text-slate-500 text-[10px] uppercase font-bold">Target Date:</span>
                  <span className="text-slate-200 font-bold text-xs">{showDate}</span>
                </div>
                <div className="flex justify-between border-b border-slate-900 pb-2">
                  <span className="text-slate-500 text-[10px] uppercase font-bold">Telegram Alert:</span>
                  <span className="text-emerald-400 font-bold text-xs">✓ DISPATCHED</span>
                </div>
                <div className="flex justify-between border-b border-slate-900 pb-2">
                  <span className="text-slate-500 text-[10px] uppercase font-bold">Response Latency:</span>
                  <span className="text-cyan-400 font-bold text-xs">{simLatency} ms</span>
                </div>
                <div className="flex flex-col space-y-1 pt-1">
                  <span className="text-slate-500 text-[10px] uppercase font-bold">Direct URL:</span>
                  <span className="text-[9px] text-slate-400 break-all bg-[#050505] border border-slate-950 p-1.5 rounded select-all leading-normal font-mono">
                    {targetUrl}
                  </span>
                </div>
              </div>

              <div className="flex">
                <a 
                  href={targetUrl}
                  target="_blank"
                  className="flex-grow flex items-center justify-center gap-1.5 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-mono font-bold rounded text-xs tracking-wider uppercase transition border border-emerald-500 cursor-pointer"
                >
                  <Globe className="w-3.5 h-3.5" />
                  <span>OPEN BOOKMYSHOW</span>
                </a>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

    </div>
  );
}
