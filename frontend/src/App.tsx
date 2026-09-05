import { useEffect, useState } from "react";
import "./App.css";

const API_URL = import.meta.env.VITE_API_URL;

function App() {
  const [watchlist, setWatchlist] = useState<any[]>([]);
  const [signals, setSignals] = useState<any[]>([]);
  const [lastChecked, setLastChecked] = useState<string | null>(null);

  const [showAddStock, setShowAddStock] = useState(false);
  const [stockSymbol, setStockSymbol] = useState("");
  const [addError, setAddError] = useState("");
  const [isAdding, setIsAdding] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Loading states
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState("");


  // ==========================================
  // FETCH MEANINGFUL SIGNALS
  // ==========================================

  const fetchSignals = async () => {
    try {
      const response = await fetch(
        `${API_URL}/api/signals`
      );

      if (!response.ok) {
        throw new Error("Failed to fetch signals");
      }

      const data = await response.json();

      setSignals(data);

    } catch (error) {
      console.error("Failed to fetch signals:", error);
    }
  };


  // ==========================================
  // INITIAL DATA LOAD WITH RETRY
  // Handles Render free-tier cold starts
  // ==========================================

  useEffect(() => {

    const loadInitialData = async () => {

      setIsLoading(true);
      setLoadError("");

      // Render can take up to ~1 minute to wake up
      const maxAttempts = 15;

      for (
        let attempt = 1;
        attempt <= maxAttempts;
        attempt++
      ) {

        try {

          const [
            watchlistResponse,
            signalsResponse,
            stateResponse
          ] = await Promise.all([
            fetch(`${API_URL}/api/watchlist`),
            fetch(`${API_URL}/api/signals`),
            fetch(`${API_URL}/api/state`)
          ]);

          if (
            !watchlistResponse.ok ||
            !signalsResponse.ok ||
            !stateResponse.ok
          ) {
            throw new Error("Backend not ready");
          }

          const watchlistData =
            await watchlistResponse.json();

          const signalsData =
            await signalsResponse.json();

          const stateData =
            await stateResponse.json();

          setWatchlist(watchlistData);
          setSignals(signalsData);
          setLastChecked(stateData.last_checked);

          setIsLoading(false);

          return;

        } catch (error) {

          console.log(
            `Waiting for backend... attempt ${attempt}/${maxAttempts}`
          );

          // Wait 5 seconds before retrying
          if (attempt < maxAttempts) {

            await new Promise((resolve) =>
              setTimeout(resolve, 5000)
            );

          }
        }
      }

      // All attempts failed
      setLoadError(
        "The market service is taking longer than expected. Please try again in a moment."
      );

      setIsLoading(false);
    };

    loadInitialData();

  }, []);


  // ==========================================
  // MARK MARKET AS CHECKED
  // ==========================================

  const markAsChecked = async () => {

    try {

      const response = await fetch(
        `${API_URL}/api/check`,
        {
          method: "POST"
        }
      );

      if (!response.ok) {
        throw new Error("Failed to mark as checked");
      }

      const data = await response.json();

      setLastChecked(data.last_checked);

      // Clear current signals
      setSignals([]);

    } catch (error) {

      console.error(
        "Failed to save check:",
        error
      );

    }
  };


  // ==========================================
  // REFRESH REAL MARKET DATA
  // ==========================================

  const refreshMarket = async () => {

    try {

      setIsRefreshing(true);

      const response = await fetch(
        `${API_URL}/api/refresh`,
        {
          method: "POST"
        }
      );

      if (!response.ok) {
        throw new Error("Failed to refresh market");
      }

      const data = await response.json();

      setWatchlist(data);

      // Fetch updated signals
      await fetchSignals();

    } catch (error) {

      console.error(
        "Failed to refresh market:",
        error
      );

    } finally {

      setIsRefreshing(false);

    }
  };


  // ==========================================
  // ADD STOCK
  // ==========================================

  const addStock = async () => {

    if (!stockSymbol.trim()) {

      setAddError(
        "Please enter a stock symbol."
      );

      return;
    }

    try {

      setIsAdding(true);
      setAddError("");

      const response = await fetch(
        `${API_URL}/api/watchlist`,
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json"
          },

          body: JSON.stringify({
            symbol: stockSymbol
          })
        }
      );

      const data = await response.json();

      if (!response.ok) {

        setAddError(
          data.detail ||
          "Could not add this stock."
        );

        return;
      }

      // Add stock immediately
      setWatchlist(
        (currentWatchlist) => [
          ...currentWatchlist,
          data
        ]
      );

      // Reset modal
      setStockSymbol("");
      setShowAddStock(false);
      setAddError("");

      // Refresh signals
      await fetchSignals();

    } catch (error) {

      console.error(
        "Failed to add stock:",
        error
      );

      setAddError(
        "Something went wrong. Please try again."
      );

    } finally {

      setIsAdding(false);

    }
  };


  return (

    <div className="app">

      {/* Navigation */}

      <nav className="navbar">

        <div className="logo">
          PULSE
          <span className="logo-dot">●</span>
        </div>

        <div className="nav-right">

          <button
            className="refresh-button"
            onClick={refreshMarket}
            disabled={isRefreshing || isLoading}
          >
            {isRefreshing
              ? "Refreshing..."
              : "↻ Refresh market"}
          </button>

          <button
            className="check-button"
            onClick={markAsChecked}
            disabled={isLoading}
          >
            ✓ Mark as checked
          </button>

          <button
            className="watchlist-button"
            disabled={isLoading}
            onClick={() => {
              setShowAddStock(true);
              setAddError("");
            }}
          >
            + Add stock
          </button>

          <div className="avatar">
            D
          </div>

        </div>

      </nav>


      {/* Main Content */}

      <main className="container">

        {/* Loading State */}

        {isLoading && (

          <div className="loading-state">

            <div className="loading-icon">
              ●
            </div>

            <h2>
              Loading your market...
            </h2>

            <p>
              Waking up the market service and fetching your watchlist.
            </p>

          </div>

        )}


        {/* Error State */}

        {loadError && (

          <div className="loading-state">

            <h2>
              Almost there.
            </h2>

            <p>
              {loadError}
            </p>

            <button
              className="refresh-button"
              onClick={() =>
                window.location.reload()
              }
            >
              Try again
            </button>

          </div>

        )}


        {/* Actual Dashboard */}

        {!isLoading && !loadError && (

          <>

            {/* Hero */}

            <section className="hero">

              <p className="eyebrow">
                YOUR MARKET, MINUS THE NOISE
              </p>

              <h1>
                Good morning, Deepika
                <span> 👋</span>
              </h1>

              <p className="subtitle">
                Here's what's changed since you last looked.
              </p>

            </section>


            {/* Summary */}

            <section className="summary-card">

              <div>

                <p className="summary-label">
                  SINCE YOUR LAST CHECK
                </p>

                <h2>

                  {signals.length === 0

                    ? "You're all caught up."

                    : `${signals.length} ${
                        signals.length === 1
                          ? "thing"
                          : "things"
                      } deserve your attention`

                  }

                </h2>

                <p className="last-checked">

                  {lastChecked

                    ? `Last checked: ${new Date(
                        lastChecked
                      ).toLocaleString(
                        "en-IN",
                        {
                          day: "2-digit",
                          month: "2-digit",
                          year: "numeric",
                          hour: "2-digit",
                          minute: "2-digit",
                          hour12: true
                        }
                      )}`

                    : "First time checking your market"

                  }

                </p>

              </div>

              <div className="summary-icon">
                {signals.length === 0
                  ? "✓"
                  : "✦"}
              </div>

            </section>


            {/* Attention Section */}

            <section className="section">

              <div className="section-header">

                <h2>
                  Worth your attention
                </h2>

                <span>
                  {signals.length}{" "}
                  {signals.length === 1
                    ? "signal"
                    : "signals"}
                </span>

              </div>


              {signals.length === 0 ? (

                <div className="empty-state">

                  <div className="empty-icon">
                    ✦
                  </div>

                  <h3>
                    You're all caught up.
                  </h3>

                  <p>
                    Nothing meaningful has changed since
                    your last check. Go touch some grass,
                    your portfolio is behaving.
                  </p>

                </div>

              ) : (

                <div className="signal-grid">

                  {signals.map((stock) => {

                    const isUp =
                      stock.change_percent >= 0;

                    return (

                      <article
                        className={`signal-card ${
                          isUp
                            ? "positive"
                            : "negative"
                        }`}
                        key={stock.symbol}
                      >

                        <div className="card-top">

                          <div>

                            <span className="signal-tag">
                              {stock.signal_type}
                            </span>

                            <h3>
                              {stock.symbol}
                            </h3>

                          </div>

                          <span className="arrow">
                            {isUp ? "↗" : "↘"}
                          </span>

                        </div>


                        <div className="price-row">

                          <span className="price">

                            ₹
                            {stock.price.toLocaleString(
                              "en-IN"
                            )}

                          </span>

                          <span
                            className={`change ${
                              isUp
                                ? "up"
                                : "down"
                            }`}
                          >

                            {isUp ? "↑" : "↓"}{" "}

                            {isUp ? "+" : ""}

                            {stock.change_percent}%

                          </span>

                        </div>


                        <div className="why">

                          <span>
                            ✦ WHY THIS MATTERS
                          </span>

                          <p>
                            {stock.reason}
                          </p>

                        </div>

                      </article>

                    );

                  })}

                </div>

              )}

            </section>


            {/* Quiet Section */}

            {signals.length > 0 && (

              <section className="quiet-card">

                <div className="quiet-icon">
                  ☁
                </div>

                <div>

                  <h3>
                    Everything else is quiet.
                  </h3>

                  <p>

                    {watchlist.length -
                      signals.length}{" "}

                    stocks haven't changed enough to
                    deserve your attention.

                  </p>

                </div>

              </section>

            )}


            {/* Watchlist */}

            <section className="section watchlist-section">

              <div className="section-header">

                <h2>
                  Your watchlist
                </h2>

                <span>
                  {watchlist.length} stocks
                </span>

              </div>


              <div className="watchlist">

                {watchlist.map((stock) => {

                  const isUp =
                    stock.change_percent >= 0;

                  return (

                    <div
                      className="stock-row"
                      key={stock.symbol}
                    >

                      <div>

                        <h3>
                          {stock.symbol}
                        </h3>

                        <p>
                          {stock.name}
                        </p>

                      </div>


                      <div className="stock-price">

                        <strong>

                          ₹
                          {stock.price.toLocaleString(
                            "en-IN"
                          )}

                        </strong>

                        <span
                          className={
                            isUp
                              ? "up"
                              : "down"
                          }
                        >

                          {isUp ? "+" : ""}
                          {stock.change_percent}%

                        </span>

                      </div>

                    </div>

                  );

                })}

              </div>

            </section>

          </>

        )}

      </main>


      {/* Add Stock Modal */}

      {showAddStock && (

        <div className="modal-overlay">

          <div className="add-stock-modal">

            <button
              className="close-button"
              onClick={() => {

                setShowAddStock(false);
                setStockSymbol("");
                setAddError("");

              }}
            >
              ×
            </button>


            <p className="modal-label">
              ADD TO WATCHLIST
            </p>

            <h2>
              Add a stock
            </h2>

            <p className="modal-subtitle">

              Enter an NSE stock symbol.
              For example: ITC, SBIN, WIPRO.

            </p>


            <input
              type="text"
              placeholder="Enter stock symbol"
              value={stockSymbol}

              onChange={(event) =>
                setStockSymbol(
                  event.target.value.toUpperCase()
                )
              }

              onKeyDown={(event) => {

                if (event.key === "Enter") {
                  addStock();
                }

              }}

              autoFocus
            />


            {addError && (

              <p className="add-error">
                {addError}
              </p>

            )}


            <button
              className="add-stock-submit"
              onClick={addStock}
              disabled={isAdding}
            >

              {isAdding
                ? "Fetching market data..."
                : "Add to watchlist"}

            </button>

          </div>

        </div>

      )}

    </div>

  );
}

export default App;
