import { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  Github, Sparkles, Plus, Search, GitPullRequest, CircleDot,
  BookOpen, Settings2, PanelLeftClose, ArrowUp, Command,
  Bot, UserRound, LoaderCircle, CheckCircle2, AlertCircle,
  Terminal, ChevronDown, Copy, ExternalLink
} from "lucide-react";

const starterPrompts = [
  { icon: Github, title: "Explore a GitHub profile", text: "Give me an overview of GitHub user teja1412" },
  { icon: GitPullRequest, title: "Review pull requests", text: "Show open pull requests for teja1412/github-developer-assistant" },
  { icon: CircleDot, title: "Find repository issues", text: "List issues in teja1412/github-developer-assistant" },
  { icon: Search, title: "Compare repositories", text: "Compare the repositories of teja1412" },
];

export default function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [activeTab, setActiveTab] = useState("Assistant");
  const [apiStatus, setApiStatus] = useState("checking");
  const [username, setUsername] = useState("teja1412");
  const [owner, setOwner] = useState("teja1412");
  const [repoName, setRepoName] = useState("github-developer-assistant");
  const [workspaceItems, setWorkspaceItems] = useState([]);
  const [workspaceLoading, setWorkspaceLoading] = useState(false);
  const [workspaceError, setWorkspaceError] = useState("");
  const bottomRef = useRef(null);
  const inputRef = useRef(null);


useEffect(() => {
  let cancelled = false;

  async function checkApi() {
    try {
      const response = await fetch("http://localhost:8000/api/health");
      const data = await response.json();

      if (!cancelled) {
        setApiStatus(data.status === "ok" ? "online" : "offline");
      }
    } catch {
      if (!cancelled) setApiStatus("offline");
    }
  }

  checkApi();

  return () => {
    cancelled = true;
  };
}, []);


  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, busy]);

  async function sendMessage(value = input) {
    const text = value.trim();
    if (!text || busy) return;
    setInput("");
    setMessages(prev => [...prev, { role: "user", content: text }]);
    setBusy(true);
    try {
      const response = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Request failed");
      setMessages(prev => [...prev, { role: "assistant", content: data.answer ?? data.response ?? String(data) }]);
    } catch (error) {
      setMessages(prev => [...prev, { role: "assistant", error: true, content: error.message }]);
    } finally {
      setBusy(false);
      inputRef.current?.focus();
    }
  }

  async function loadWorkspace(tab, values = {}) {
    setActiveTab(tab);
    setWorkspaceError("");
    setWorkspaceItems([]);
    setWorkspaceLoading(true);

    const params = new URLSearchParams();
    let endpoint;
    let resultKey;

    if (tab === "Repositories") {
      const requestedUsername = (values.username ?? username).trim();
      if (!requestedUsername) {
        setWorkspaceError("Enter a GitHub username.");
        setWorkspaceLoading(false);
        return;
      }
      setUsername(requestedUsername);
      params.set("username", requestedUsername);
      endpoint = "/api/repos";
      resultKey = "repositories";
    } else {
      const requestedOwner = (values.owner ?? owner).trim();
      const requestedRepo = (values.repo ?? repoName).trim();
      if (!requestedOwner || !requestedRepo) {
        setWorkspaceError("Enter both a repository owner and name.");
        setWorkspaceLoading(false);
        return;
      }
      setOwner(requestedOwner);
      setRepoName(requestedRepo);
      params.set("owner", requestedOwner);
      params.set("repo", requestedRepo);
      endpoint = tab === "Issues" ? "/api/issues" : "/api/pulls";
      resultKey = tab === "Issues" ? "issues" : "pull_requests";
    }

    try {
      const response = await fetch(`http://localhost:8000${endpoint}?${params}`);
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Request failed");

      const items = data[resultKey];
      if (items?.error) throw new Error(items.error);
      setWorkspaceItems(
        Array.isArray(items) ? items : items && typeof items === "object" ? [items] : []
      );
    } catch (error) {
      setWorkspaceError(error.message || "Unable to load GitHub data.");
    } finally {
      setWorkspaceLoading(false);
    }
  }

  function openRepositoryTab(tab, repository) {
    const repositoryOwner = repository.owner || repository.full_name?.split("/")[0] || username;
    const repositoryName = repository.name || repository.full_name?.split("/")[1];
    if (!repositoryName) return;

    setOwner(repositoryOwner);
    setRepoName(repositoryName);
    loadWorkspace(tab, { owner: repositoryOwner, repo: repositoryName });
  }

  function newChat() {
    setMessages([]);
    setInput("");
    inputRef.current?.focus();
  }

  function renderWorkspaceItems() {
    if (workspaceLoading) {
      return <div className="workspace-message"><LoaderCircle className="spin" size={18}/> Loading {activeTab.toLowerCase()}…</div>;
    }
    if (workspaceError) {
      return <div className="workspace-message workspace-error"><AlertCircle size={18}/>{workspaceError}</div>;
    }
    if (!workspaceItems.length) {
      return <div className="workspace-message">No {activeTab.toLowerCase()} found.</div>;
    }

    return (
      <div className="workspace-grid">
        {workspaceItems.map((item, index) => {
          const title = item.full_name || item.title || item.name || `#${item.number}`;
          const url = item.html_url;
          const description = item.description || item.body;
          return (
            <article className="workspace-card" key={item.id ?? item.number ?? title ?? index}>
              <div className="workspace-card-heading">
                <h2>{url ? <a href={url} target="_blank" rel="noreferrer">{title}</a> : title}</h2>
                {url && <a className="workspace-link" href={url} target="_blank" rel="noreferrer" aria-label={`Open ${title} on GitHub`}><ExternalLink size={15}/></a>}
              </div>
              {description && <p>{description}</p>}
              <div className="workspace-meta">
                {activeTab === "Repositories" ? (
                  <>
                    {item.language && <span>{item.language}</span>}
                    <span>★ {item.stargazers_count ?? 0}</span>
                    <span>{item.private ? "Private" : "Public"}</span>
                    <button type="button" onClick={() => openRepositoryTab("Issues", item)}>Issues</button>
                    <button type="button" onClick={() => openRepositoryTab("Pull requests", item)}>Pull requests</button>
                  </>
                ) : (
                  <>
                    {item.number != null && <span>#{item.number}</span>}
                    {item.state && <span className={`item-state ${item.state}`}>{item.state}</span>}
                    {item.user && <span>by {item.user}</span>}
                    {item.draft && <span>Draft</span>}
                    {item.updated_at && <span>Updated {new Date(item.updated_at).toLocaleDateString()}</span>}
                  </>
                )}
              </div>
            </article>
          );
        })}
      </div>
    );
  }

  return (
    <div className="app-shell">
      <aside className={`sidebar ${sidebarOpen ? "" : "collapsed"}`}>
        <div className="brand-row">
          <div className="brand-mark"><Github size={20} /></div>
          {sidebarOpen && <div className="brand-copy"><b>GitHub<span>AI</span></b><small>Developer assistant</small></div>}
          <button className="icon-button collapse-btn" onClick={() => setSidebarOpen(v => !v)} title="Toggle sidebar"><PanelLeftClose size={17}/></button>
        </div>
        <button className="new-chat" onClick={newChat}><Plus size={17}/>{sidebarOpen && " New conversation"}{sidebarOpen && <span className="shortcut">⌘ K</span>}</button>
        {sidebarOpen && <>
          <div className="side-label">WORKSPACE</div>
          <button className={`nav-item ${activeTab === "Assistant" ? "selected" : ""}`} onClick={() => setActiveTab("Assistant")}><Sparkles size={17}/> Assistant</button>
          <button className={`nav-item ${activeTab === "Repositories" ? "selected" : ""}`} onClick={() => loadWorkspace("Repositories")}><BookOpen size={17}/> Repositories</button>
          <button className={`nav-item ${activeTab === "Pull requests" ? "selected" : ""}`} onClick={() => loadWorkspace("Pull requests")}><GitPullRequest size={17}/> Pull requests</button>
          <button className={`nav-item ${activeTab === "Issues" ? "selected" : ""}`} onClick={() => loadWorkspace("Issues")}><CircleDot size={17}/> Issues</button>
          <div className="side-label recent-label">RECENT</div>
          {messages.filter(m => m.role === "user").slice(-5).reverse().map((m, i) => <button key={i} className="history-item" onClick={() => setInput(m.content)}>{m.content}</button>)}
          <div className="sidebar-bottom">
            <div className="connection"><span className={`status-dot ${apiStatus}`}/><span>{apiStatus === "online" ? "API connected" : apiStatus === "checking" ? "Connecting…" : "API offline"}</span></div>
            <button className="nav-item"><Settings2 size={17}/> Settings</button>
            <div className="profile"><div className="avatar">DT</div><div><b>Developer</b><small>GitHub workspace</small></div><ChevronDown size={15}/></div>
          </div>
        </>}
      </aside>

      <main className="main-panel">
        <header className="topbar">
          <div className="top-left"><span className="mobile-brand"><Github size={18}/></span><span className="crumb">Workspace</span><span className="crumb-slash">/</span><b>{activeTab}</b></div>
          <div className="top-right"><span className="model-pill"><span className="model-dot"/> Gemini · MCP</span><button className="icon-button" title="Command"><Command size={16}/></button></div>
        </header>

        <section className={`conversation ${activeTab === "Assistant" && messages.length === 0 ? "empty" : ""}`}>
          {activeTab !== "Assistant" ? (
            <div className="workspace-view">
              <div className="workspace-header">
                <div>
                  <div className="eyebrow"><span/> GITHUB WORKSPACE</div>
                  <h1>{activeTab}</h1>
                  <p>{activeTab === "Repositories" ? "Browse a GitHub user's public repositories." : `Browse ${activeTab.toLowerCase()} for a repository.`}</p>
                </div>
              </div>
              <form className="workspace-search" onSubmit={event => {
                event.preventDefault();
                loadWorkspace(activeTab);
              }}>
                {activeTab === "Repositories" ? (
                  <label>
                    <span>GitHub username</span>
                    <input value={username} onChange={event => setUsername(event.target.value)} placeholder="e.g. teja1412"/>
                  </label>
                ) : (
                  <>
                    <label>
                      <span>Owner</span>
                      <input value={owner} onChange={event => setOwner(event.target.value)} placeholder="e.g. octocat"/>
                    </label>
                    <label>
                      <span>Repository</span>
                      <input value={repoName} onChange={event => setRepoName(event.target.value)} placeholder="e.g. hello-world"/>
                    </label>
                  </>
                )}
                <button className="workspace-submit" type="submit" disabled={workspaceLoading}>
                  {workspaceLoading ? <LoaderCircle size={16} className="spin"/> : <Search size={16}/>}
                  {workspaceLoading ? "Loading…" : "Load"}
                </button>
              </form>
              {renderWorkspaceItems()}
            </div>
          ) : messages.length === 0 ? (
            <div className="welcome">
              <div className="hero-orb"><div className="orb-inner"><Github size={34}/></div><span className="orb-spark"><Sparkles size={15}/></span></div>
              <div className="eyebrow"><span/> YOUR GITHUB COPILOT</div>
              <h1>Build better.<br/><em>Ship smarter.</em></h1>
              <p className="welcome-copy">Your GitHub workspace, understood.<br/>Ask about repositories, issues, pull requests, and more.</p>
              <div className="prompt-grid">
                {starterPrompts.map(({icon: Icon, title, text}) => <button className="prompt-card" key={title} onClick={() => sendMessage(text)}><span className="prompt-icon"><Icon size={17}/></span><span><b>{title}</b><small>{text}</small></span><ArrowUp className="prompt-arrow" size={15}/></button>)}
              </div>
              <div className="welcome-foot"><span className="tiny-check"><CheckCircle2 size={13}/></span> Connected to your MCP-powered GitHub tools</div>
            </div>
          ) : (
            <div className="message-list">
              {messages.map((message, index) => <article className={`message ${message.role}`} key={index}>
                <div className={`message-avatar ${message.role}`}>{message.role === "user" ? <UserRound size={16}/> : <Sparkles size={16}/>}</div>
                <div className="message-content">
                  <div className="message-name">{message.role === "user" ? "You" : "GitHub Assistant"}{message.error && <span className="error-label"><AlertCircle size={12}/> Error</span>}</div>
                  {message.role === "assistant" ? (
                    <div className="markdown">
                      <ReactMarkdown
                        remarkPlugins={[remarkGfm]}
                        components={{
                          table: ({ children }) => (
                            <div className="markdown-table-wrap">
                              <table>{children}</table>
                            </div>
                          ),
                        }}
                      >
                        {message.content}
                      </ReactMarkdown>
                    </div>
                  ) : <p>{message.content}</p>}
                </div>
              </article>)}
              {busy && <article className="message assistant"><div className="message-avatar assistant"><Sparkles size={16}/></div><div className="message-content"><div className="message-name">GitHub Assistant</div><div className="thinking"><LoaderCircle size={15}/> Thinking and checking GitHub tools<span className="thinking-dots">•••</span></div></div></article>}
              <div ref={bottomRef}/>
            </div>
          )}
        </section>

        {activeTab === "Assistant" && <footer className="composer-area">
          <div className="composer">
            <textarea ref={inputRef} value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => {if(e.key === "Enter" && !e.shiftKey){e.preventDefault();sendMessage();}}} placeholder="Ask anything about GitHub…" rows={1}/>
            <div className="composer-bottom"><div className="composer-hint"><span className="kbd">↵</span> to send <span className="hint-divider">·</span> <span className="kbd">⇧ ↵</span> new line</div><button className="send-button" disabled={!input.trim() || busy} onClick={() => sendMessage()} title="Send message">{busy ? <LoaderCircle size={17} className="spin"/> : <ArrowUp size={18}/>}</button></div>
          </div>
          <div className="disclaimer"><Sparkles size={12}/> AI can make mistakes. Verify important GitHub details.</div>
        </footer>}
      </main>
    </div>
  );
}
