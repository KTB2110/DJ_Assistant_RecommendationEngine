import { useState, useEffect } from 'react'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

function App() {
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])

  // Current track loaded in each deck (for preview/sampling)
  const [deckACurrent, setDeckACurrent] = useState(null)
  const [deckBCurrent, setDeckBCurrent] = useState(null)

  // Playlists (committed tracks)
  const [deckAPlaylist, setDeckAPlaylist] = useState([])
  const [deckBPlaylist, setDeckBPlaylist] = useState([])

  // Master setlist (interleaved A1, B1, A2, B2...)
  const [masterSetlist, setMasterSetlist] = useState([])

  // Recommendations
  const [recommendations, setRecommendations] = useState([])

  // Recommendation source toggle (which deck to base recommendations on)
  const [recommendationSource, setRecommendationSource] = useState('A')

  // Graph panel visibility
  const [showGraphs, setShowGraphs] = useState(false)

  // Settings panel visibility
  const [showSettings, setShowSettings] = useState(true)

  // Deck playlist visibility
  const [showDeckAPlaylist, setShowDeckAPlaylist] = useState(false)
  const [showDeckBPlaylist, setShowDeckBPlaylist] = useState(false)

  // Advanced mode toggle
  const [showAdvanced, setShowAdvanced] = useState(false)

  // Main direction controls
  const [bpmDirection, setBpmDirection] = useState('maintain')
  const [energyDirection, setEnergyDirection] = useState('maintain')

  // Advanced feature directions
  const [featureDirections, setFeatureDirections] = useState({
    danceability: 'maintain',
    valence: 'maintain',
    acousticness: 'maintain',
    instrumentalness: 'maintain',
    speechiness: 'maintain',
    liveness: 'maintain',
    loudness: 'maintain'
  })

  // Genre filter
  const [selectedGenres, setSelectedGenres] = useState([])
  const [suggestedGenres, setSuggestedGenres] = useState([])
  const [showGenreDropdown, setShowGenreDropdown] = useState(false)
  const [allGenres, setAllGenres] = useState([])

  // Loading state for refresh button
  const [isRefreshing, setIsRefreshing] = useState(false)

  // Tutorial visibility
  const [showTutorial, setShowTutorial] = useState(true)

  // Camelot wheel mapping
  const SPOTIFY_TO_CAMELOT = {
    '0,0': '5A', '1,0': '12A', '2,0': '7A', '3,0': '2A', '4,0': '9A', '5,0': '4A',
    '6,0': '11A', '7,0': '6A', '8,0': '1A', '9,0': '8A', '10,0': '3A', '11,0': '10A',
    '0,1': '8B', '1,1': '3B', '2,1': '10B', '3,1': '5B', '4,1': '12B', '5,1': '7B',
    '6,1': '2B', '7,1': '9B', '8,1': '4B', '9,1': '11B', '10,1': '6B', '11,1': '1B'
  }

  const MUSICAL_KEYS = {
    '0,0': 'C minor', '1,0': 'C# minor', '2,0': 'D minor', '3,0': 'D# minor',
    '4,0': 'E minor', '5,0': 'F minor', '6,0': 'F# minor', '7,0': 'G minor',
    '8,0': 'G# minor', '9,0': 'A minor', '10,0': 'A# minor', '11,0': 'B minor',
    '0,1': 'C major', '1,1': 'C# major', '2,1': 'D major', '3,1': 'D# major',
    '4,1': 'E major', '5,1': 'F major', '6,1': 'F# major', '7,1': 'G major',
    '8,1': 'G# major', '9,1': 'A major', '10,1': 'A# major', '11,1': 'B major'
  }

  // Fetch all genres on mount
  useEffect(() => {
    const fetchGenres = async () => {
      const response = await fetch(`${API_URL}/genres`)
      const data = await response.json()
      setAllGenres(data)
    }
    fetchGenres()
  }, [])

  // Get the current source track based on toggle
  const getSourceTrack = () => {
    return recommendationSource === 'A' ? deckACurrent : deckBCurrent
  }

  // Get the target deck (opposite of source)
  const getTargetDeck = () => {
    return recommendationSource === 'A' ? 'B' : 'A'
  }

  const getCamelotKey = (track) => {
    if (!track) return 'N/A'
    const key = `${track.key},${track.mode}`
    return SPOTIFY_TO_CAMELOT[key] || 'Unknown'
  }

  const getMusicalKey = (track) => {
    if (!track) return 'N/A'
    const key = `${track.key},${track.mode}`
    return MUSICAL_KEYS[key] || 'Unknown'
  }

  // Check if track is already in a playlist
  const getTrackPlaylistStatus = (track) => {
    const trackKey = `${track.track_name.toLowerCase()}-${track.artists.toLowerCase()}`
    
    const inDeckA = deckAPlaylist.some(t => 
      `${t.track_name.toLowerCase()}-${t.artists.toLowerCase()}` === trackKey
    )
    const inDeckB = deckBPlaylist.some(t => 
      `${t.track_name.toLowerCase()}-${t.artists.toLowerCase()}` === trackKey
    )
    
    if (inDeckA) return 'A'
    if (inDeckB) return 'B'
    return null
  }

  // Load track from playlist back to deck
  const loadFromPlaylistA = (track) => {
    setDeckACurrent(track)
  }

  const loadFromPlaylistB = (track) => {
    setDeckBCurrent(track)
  }

  // Remove track from Deck A playlist
  const removeFromDeckA = (index) => {
    const removedTrack = deckAPlaylist[index]
    setDeckAPlaylist(prev => prev.filter((_, i) => i !== index))
    
    // Also remove from master setlist
    setMasterSetlist(prev => prev.filter(item => 
      !(item.deck === 'A' && item.track.track_id === removedTrack.track_id)
    ))
  }

  // Remove track from Deck B playlist
  const removeFromDeckB = (index) => {
    const removedTrack = deckBPlaylist[index]
    setDeckBPlaylist(prev => prev.filter((_, i) => i !== index))
    
    // Also remove from master setlist
    setMasterSetlist(prev => prev.filter(item => 
      !(item.deck === 'B' && item.track.track_id === removedTrack.track_id)
    ))
  }

  // Reset all settings to defaults
  const resetSettings = () => {
    setBpmDirection('maintain')
    setEnergyDirection('maintain')
    setFeatureDirections({
      danceability: 'maintain',
      valence: 'maintain',
      acousticness: 'maintain',
      instrumentalness: 'maintain',
      speechiness: 'maintain',
      liveness: 'maintain',
      loudness: 'maintain'
    })
    setSelectedGenres([])
    setSuggestedGenres([])
  }

  // Direction toggle component
  const DirectionToggle = ({ label, value, onChange, type = 'default' }) => {
    const labels = type === 'bpm' 
      ? ['Slower', 'Maintain', 'Faster']
      : ['Drop', 'Maintain', 'Build']
    
    const values = type === 'bpm'
      ? ['slower', 'maintain', 'faster']
      : ['drop', 'maintain', 'build']

    return (
      <div className="flex flex-col gap-2">
        <span className="text-spotify-lightgray text-sm">{label}</span>
        <div className="flex bg-spotify-gray rounded-full p-1">
          <button
            onClick={() => onChange(values[0])}
            className={`px-3 py-1 rounded-full text-sm transition ${
              value === values[0]
                ? 'bg-red-500 text-white' 
                : 'text-spotify-lightgray hover:text-white'
            }`}
          >
            {labels[0]}
          </button>
          <button
            onClick={() => onChange(values[1])}
            className={`px-3 py-1 rounded-full text-sm transition ${
              value === values[1]
                ? 'bg-spotify-green text-black' 
                : 'text-spotify-lightgray hover:text-white'
            }`}
          >
            {labels[1]}
          </button>
          <button
            onClick={() => onChange(values[2])}
            className={`px-3 py-1 rounded-full text-sm transition ${
              value === values[2]
                ? 'bg-blue-500 text-white' 
                : 'text-spotify-lightgray hover:text-white'
            }`}
          >
            {labels[2]}
          </button>
        </div>
      </div>
    )
  }

  // Update a single feature direction
  const updateFeatureDirection = (feature, direction) => {
    setFeatureDirections(prev => ({
      ...prev,
      [feature]: direction
    }))
  }

  // Fetch recommendations with current settings
  const fetchRecommendations = async (track) => {
    if (!track) return
    
    setIsRefreshing(true)
    const response = await fetch(`${API_URL}/recommend`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        track, 
        limit: 10,
        bpm_direction: bpmDirection,
        energy_direction: energyDirection,
        feature_directions: showAdvanced ? featureDirections : null,
        genre_filter: selectedGenres.length > 0 ? selectedGenres : null
      })
    })
    const data = await response.json()
    setRecommendations(data)
    setIsRefreshing(false)
  }

  // Suggest similar genres based on source track
  const suggestGenres = async () => {
    const track = getSourceTrack()
    if (!track) return
    
    const response = await fetch(`${API_URL}/genres/${track.track_genre}/similar?top_k=5`)
    const data = await response.json()
    
    // Include current genre + similar ones
    const genres = [track.track_genre, ...data.map(g => g.genre)]
    setSuggestedGenres(data)
    setSelectedGenres(genres)
  }

  // Search for tracks
  const handleSearch = async () => {
    if (!searchQuery.trim()) return
    
    const response = await fetch(`${API_URL}/search?query=${encodeURIComponent(searchQuery)}&limit=10`)
    const data = await response.json()
    setSearchResults(data)
  }

  // Load track to Deck A for preview
  const loadToDeckA = async (track) => {
    setDeckACurrent(track)
    setSearchResults([])
    setSearchQuery('')
    setRecommendationSource('A')
    
    await fetchRecommendations(track)
  }

  // Load recommendation to the target deck
  const loadRecommendation = async (rec) => {
    const track = rec.track || rec
    
    if (recommendationSource === 'A') {
      setDeckBCurrent(track)
    } else {
      setDeckACurrent(track)
    }
  }

  // Refresh recommendations with current settings
  const refreshRecommendations = async () => {
    const track = getSourceTrack()
    if (!track) return
    
    await fetchRecommendations(track)
  }

  // Switch recommendation source and fetch new recommendations
  const switchRecommendationSource = async (source) => {
    setRecommendationSource(source)
    const track = source === 'A' ? deckACurrent : deckBCurrent
    if (track) {
      await fetchRecommendations(track)
    }
  }

  // Add current deck track to its playlist
  const addToDeckA = () => {
    if (!deckACurrent) return
    
    setDeckAPlaylist(prev => [...prev, deckACurrent])
    
    setMasterSetlist(prev => [...prev, {
      track: deckACurrent,
      deck: 'A',
      order: prev.length + 1
    }])
    
    // Reset settings and switch to recommend for Deck A (next track goes to B)
    resetSettings()
    setRecommendationSource('A')
  }

  const addToDeckB = () => {
    if (!deckBCurrent) return
    
    setDeckBPlaylist(prev => [...prev, deckBCurrent])
    
    setMasterSetlist(prev => [...prev, {
      track: deckBCurrent,
      deck: 'B',
      order: prev.length + 1
    }])
    
    // Reset settings and switch to recommend for Deck B (next track goes to A)
    resetSettings()
    setRecommendationSource('B')
  }

  return (
    <div className="min-h-screen bg-spotify-black text-spotify-white">
      {/* Header */}
      <header className="bg-spotify-darkgray p-6 border-b border-spotify-gray flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-spotify-green">DJ Assistant</h1>
          <p className="text-spotify-lightgray text-sm mt-1">Plan your perfect setlist</p>
        </div>
        <button
          onClick={() => setShowGraphs(!showGraphs)}
          className="bg-spotify-gray px-4 py-2 rounded-full hover:bg-spotify-lightgray hover:text-black transition"
        >
          {showGraphs ? 'Hide Graphs' : 'Show Graphs'} ({masterSetlist.length} tracks)
        </button>
      </header>

      {/* Tutorial Section */}
      <div className="px-6 pt-6">
        <div className="bg-spotify-darkgray rounded-lg mb-6">
          {/* Tutorial Header */}
          <div 
            className="flex justify-between items-center p-4 cursor-pointer hover:bg-spotify-gray rounded-t-lg transition"
            onClick={() => setShowTutorial(!showTutorial)}
          >
            <div className="flex items-center gap-2">
              <span className="text-2xl">🎧</span>
              <h3 className="text-lg font-semibold">Quick Start Tutorial</h3>
            </div>
            <span className="text-spotify-lightgray">{showTutorial ? '▲ Hide' : '▼ Show'}</span>
          </div>

          {/* Tutorial Content */}
          {showTutorial && (
            <div className="p-4 pt-0 border-t border-spotify-gray">
              <div className="space-y-4">
                <div className="flex gap-4 items-start">
                  <div className="bg-spotify-green text-black font-bold rounded-full w-8 h-8 flex items-center justify-center text-sm flex-shrink-0">
                    1
                  </div>
                  <div>
                    <h4 className="font-semibold text-spotify-green mb-1">Search for Your Starting Track</h4>
                    <p className="text-spotify-lightgray text-sm">Use the search bar below to find your first song. Type the track name or artist and hit Enter or click Search.</p>
                  </div>
                </div>

                <div className="flex gap-4 items-start">
                  <div className="bg-spotify-green text-black font-bold rounded-full w-8 h-8 flex items-center justify-center text-sm flex-shrink-0">
                    2
                  </div>
                  <div>
                    <h4 className="font-semibold text-spotify-green mb-1">Load Into Deck A</h4>
                    <p className="text-spotify-lightgray text-sm">Click on any search result to load it into Deck A. The track will appear with its details and Spotify preview.</p>
                  </div>
                </div>

                <div className="flex gap-4 items-start">
                  <div className="bg-spotify-green text-black font-bold rounded-full w-8 h-8 flex items-center justify-center text-sm flex-shrink-0">
                    3
                  </div>
                  <div>
                    <h4 className="font-semibold text-spotify-green mb-1">Get AI Recommendations</h4>
                    <p className="text-spotify-lightgray text-sm">Recommendations will automatically appear at the bottom of the page. These are AI-generated suggestions that mix well with your selected track.</p>
                  </div>
                </div>

                <div className="flex gap-4 items-start">
                  <div className="bg-spotify-green text-black font-bold rounded-full w-8 h-8 flex items-center justify-center text-sm flex-shrink-0">
                    4
                  </div>
                  <div>
                    <h4 className="font-semibold text-spotify-green mb-1">Choose Your Next Track</h4>
                    <p className="text-spotify-lightgray text-sm">Click any recommendation to load it into Deck B. You can preview the track and see how it matches with your current selection.</p>
                  </div>
                </div>

                <div className="flex gap-4 items-start">
                  <div className="bg-spotify-green text-black font-bold rounded-full w-8 h-8 flex items-center justify-center text-sm flex-shrink-0">
                    5
                  </div>
                  <div>
                    <h4 className="font-semibold text-spotify-green mb-1">Control Your Mix Direction</h4>
                    <p className="text-spotify-lightgray text-sm">Use the <strong>Recommendation Settings</strong> to control genre preferences and how the energy/BPM should evolve (build up, drop down, or maintain).</p>
                  </div>
                </div>

                <div className="flex gap-4 items-start">
                  <div className="bg-spotify-green text-black font-bold rounded-full w-8 h-8 flex items-center justify-center text-sm flex-shrink-0">
                    6
                  </div>
                  <div>
                    <h4 className="font-semibold text-spotify-green mb-1">Advanced Fine-Tuning</h4>
                    <p className="text-spotify-lightgray text-sm">Click <strong>"Show Advanced"</strong> in Recommendation Settings for granular control over features like danceability, valence, acousticness, and more.</p>
                  </div>
                </div>

                <div className="flex gap-4 items-start">
                  <div className="bg-spotify-green text-black font-bold rounded-full w-8 h-8 flex items-center justify-center text-sm flex-shrink-0">
                    7
                  </div>
                  <div>
                    <h4 className="font-semibold text-spotify-green mb-1">Build Your Setlist</h4>
                    <p className="text-spotify-lightgray text-sm">Click <strong>"Add to Deck"</strong> to commit tracks to your playlist. This builds your master setlist in the order A1, B1, A2, B2...</p>
                  </div>
                </div>

                <div className="flex gap-4 items-start">
                  <div className="bg-spotify-green text-black font-bold rounded-full w-8 h-8 flex items-center justify-center text-sm flex-shrink-0">
                    8
                  </div>
                  <div>
                    <h4 className="font-semibold text-spotify-green mb-1">Visualize Your Flow</h4>
                    <p className="text-spotify-lightgray text-sm">Click <strong>"Show Graphs"</strong> in the top-right to see how your setlist flows in terms of energy, tempo, and other musical features.</p>
                  </div>
                </div>

                <div className="bg-spotify-gray rounded-lg p-3 mt-4">
                  <p className="text-spotify-lightgray text-xs">
                    <strong>Pro Tip:</strong> The system automatically switches recommendation sources after each "Add to Deck" action to help you build a flowing setlist that alternates between the two decks.
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Search */}
      <div className="px-6 pb-6">
        <div className="flex gap-4 max-w-xl">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            placeholder="Search for a track..."
            className="flex-1 bg-spotify-gray text-white px-4 py-3 rounded-full outline-none focus:ring-2 focus:ring-spotify-green"
          />
          <button
            onClick={handleSearch}
            className="bg-spotify-green text-black font-semibold px-6 py-3 rounded-full hover:bg-green-400 transition active:scale-95"
          >
            Search
          </button>
        </div>

        {/* Dataset Info Note */}
        <div className="mt-3 max-w-xl text-xs text-spotify-lightgray">
          <p>
            🎵 This recommendation engine uses ~90k songs from the{' '}
            <a 
              href="https://huggingface.co/datasets/maharshipandya/spotify-tracks-dataset" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-spotify-green hover:underline"
            >
              Maharshipandya Spotify Tracks Dataset
            </a>
            . If a song isn't showing up, please try a different one. Note: Spotify previews are unavailable for a small subset of tracks but should be available for most.
          </p>
        </div>

        {/* Search Results */}
        {searchResults.length > 0 && (
          <div className="mt-4 bg-spotify-darkgray rounded-lg p-4 max-w-xl">
            <h3 className="text-sm text-spotify-lightgray mb-2">Search Results</h3>
            {searchResults.map((track, i) => (
              <div
                key={i}
                onClick={() => loadToDeckA(track)}
                className="p-3 hover:bg-spotify-gray active:bg-spotify-lightgray rounded cursor-pointer flex justify-between items-center transition-colors"
              >
                <div>
                  <p className="font-medium">{track.track_name}</p>
                  <p className="text-sm text-spotify-lightgray">{track.artists}</p>
                </div>
                <span className="text-spotify-lightgray text-sm">{Math.round(track.tempo)} BPM</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Decks */}
      <div className="p-6 grid grid-cols-2 gap-6">
        {/* Deck A */}
        <div className={`bg-spotify-darkgray rounded-lg overflow-hidden transition-all ${
          getTargetDeck() === 'A' ? 'ring-2 ring-spotify-green ring-opacity-50' : ''
        }`}>
          {/* Top Half - Controls */}
          <div className="p-6 border-b border-spotify-gray">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold text-spotify-green">Deck A</h2>
              <button
                onClick={() => setShowDeckAPlaylist(!showDeckAPlaylist)}
                className="text-spotify-lightgray text-sm hover:text-white transition"
              >
                {deckAPlaylist.length} tracks {showDeckAPlaylist ? '▲' : '▼'}
              </button>
            </div>

            {/* Collapsible Playlist */}
            {showDeckAPlaylist && deckAPlaylist.length > 0 && (
              <div className="mb-4 bg-spotify-black rounded-lg p-3 max-h-40 overflow-y-auto">
                {deckAPlaylist.map((track, i) => (
                  <div 
                    key={i} 
                    className="text-sm py-2 border-b border-spotify-gray last:border-0 flex justify-between items-center group"
                  >
                    <div 
                      className="flex-1 cursor-pointer hover:text-spotify-green transition"
                      onClick={() => loadFromPlaylistA(track)}
                    >
                      <span className="text-spotify-lightgray">{i + 1}.</span> {track.track_name}
                      <span className="text-spotify-lightgray text-xs ml-2">- {track.artists}</span>
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        removeFromDeckA(i)
                      }}
                      className="text-spotify-lightgray hover:text-red-500 opacity-0 group-hover:opacity-100 transition ml-2"
                    >
                      ✕
                    </button>
                  </div>
                ))}
              </div>
            )}
            
            {deckACurrent ? (
              <div>
                <p className="text-lg font-medium">{deckACurrent.track_name}</p>
                <p className="text-spotify-lightgray">{deckACurrent.artists}</p>
                <div className="mt-4 grid grid-cols-2 gap-2 text-sm">
                  <div className="bg-spotify-gray p-2 rounded">
                    <span className="text-spotify-lightgray">BPM:</span> {Math.round(deckACurrent.tempo)}
                  </div>
                  <div className="bg-spotify-gray p-2 rounded">
                    <span className="text-spotify-lightgray">Energy:</span> {(deckACurrent.energy * 100).toFixed(0)}%
                  </div>
                  <div className="bg-spotify-gray p-2 rounded">
                    <span className="text-spotify-lightgray">Genre:</span> {deckACurrent.track_genre}
                  </div>
                  <div className="bg-spotify-gray p-2 rounded">
                    <span className="text-spotify-lightgray">Camelot:</span> {getCamelotKey(deckACurrent)}
                  </div>
                  <div className="bg-spotify-gray p-2 rounded col-span-2">
                    <span className="text-spotify-lightgray">Key:</span> {getMusicalKey(deckACurrent)}
                  </div>
                </div>
                
                {/* Buttons */}
                <div className="mt-4 flex gap-2">
                  <button
                    onClick={addToDeckA}
                    className="flex-1 bg-spotify-green text-black font-semibold py-2 rounded-full hover:bg-green-400 transition active:scale-95 active:bg-green-600"
                  >
                    ✓ Add to Deck A
                  </button>
                </div>
              </div>
            ) : (
              <p className="text-spotify-lightgray">Search and select a track</p>
            )}
          </div>
          
          {/* Bottom Half - Spotify Embed */}
          <div className="p-4 bg-spotify-black">
            {deckACurrent ? (
              <iframe
                src={`https://open.spotify.com/embed/track/${deckACurrent.track_id}`}
                width="100%"
                height="152"
                frameBorder="0"
                allow="encrypted-media"
                className="rounded"
              />
            ) : (
              <div className="h-[152px] flex items-center justify-center text-spotify-lightgray">
                No track loaded
              </div>
            )}
          </div>
        </div>

        {/* Deck B */}
        <div className={`bg-spotify-darkgray rounded-lg overflow-hidden transition-all ${
          getTargetDeck() === 'B' ? 'ring-2 ring-spotify-green ring-opacity-50' : ''
        }`}>
          {/* Top Half - Controls */}
          <div className="p-6 border-b border-spotify-gray">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold text-spotify-green">Deck B</h2>
              <button
                onClick={() => setShowDeckBPlaylist(!showDeckBPlaylist)}
                className="text-spotify-lightgray text-sm hover:text-white transition"
              >
                {deckBPlaylist.length} tracks {showDeckBPlaylist ? '▲' : '▼'}
              </button>
            </div>

            {/* Collapsible Playlist */}
            {showDeckBPlaylist && deckBPlaylist.length > 0 && (
              <div className="mb-4 bg-spotify-black rounded-lg p-3 max-h-40 overflow-y-auto">
                {deckBPlaylist.map((track, i) => (
                  <div 
                    key={i} 
                    className="text-sm py-2 border-b border-spotify-gray last:border-0 flex justify-between items-center group"
                  >
                    <div 
                      className="flex-1 cursor-pointer hover:text-spotify-green transition"
                      onClick={() => loadFromPlaylistB(track)}
                    >
                      <span className="text-spotify-lightgray">{i + 1}.</span> {track.track_name}
                      <span className="text-spotify-lightgray text-xs ml-2">- {track.artists}</span>
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        removeFromDeckB(i)
                      }}
                      className="text-spotify-lightgray hover:text-red-500 opacity-0 group-hover:opacity-100 transition ml-2"
                    >
                      ✕
                    </button>
                  </div>
                ))}
              </div>
            )}
            
            {deckBCurrent ? (
              <div>
                <p className="text-lg font-medium">{deckBCurrent.track_name}</p>
                <p className="text-spotify-lightgray">{deckBCurrent.artists}</p>
                <div className="mt-4 grid grid-cols-2 gap-2 text-sm">
                  <div className="bg-spotify-gray p-2 rounded">
                    <span className="text-spotify-lightgray">BPM:</span> {Math.round(deckBCurrent.tempo)}
                  </div>
                  <div className="bg-spotify-gray p-2 rounded">
                    <span className="text-spotify-lightgray">Energy:</span> {(deckBCurrent.energy * 100).toFixed(0)}%
                  </div>
                  <div className="bg-spotify-gray p-2 rounded">
                    <span className="text-spotify-lightgray">Genre:</span> {deckBCurrent.track_genre}
                  </div>
                  <div className="bg-spotify-gray p-2 rounded">
                    <span className="text-spotify-lightgray">Camelot:</span> {getCamelotKey(deckBCurrent)}
                  </div>
                  <div className="bg-spotify-gray p-2 rounded col-span-2">
                    <span className="text-spotify-lightgray">Key:</span> {getMusicalKey(deckBCurrent)}
                  </div>
                </div>
                
                {/* Buttons */}
                <div className="mt-4 flex gap-2">
                  <button
                    onClick={addToDeckB}
                    className="flex-1 bg-spotify-green text-black font-semibold py-2 rounded-full hover:bg-green-400 transition active:scale-95 active:bg-green-600"
                  >
                    ✓ Add to Deck B
                  </button>
                </div>
              </div>
            ) : (
              <p className="text-spotify-lightgray">Select a recommendation</p>
            )}
          </div>
          
          {/* Bottom Half - Spotify Embed */}
          <div className="p-4 bg-spotify-black">
            {deckBCurrent ? (
              <iframe
                src={`https://open.spotify.com/embed/track/${deckBCurrent.track_id}`}
                width="100%"
                height="152"
                frameBorder="0"
                allow="encrypted-media"
                className="rounded"
              />
            ) : (
              <div className="h-[152px] flex items-center justify-center text-spotify-lightgray">
                No track loaded
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Recommendation Settings - Now below decks */}
      <div className="px-6 pb-6">
        <div className="bg-spotify-darkgray rounded-lg">
          {/* Header - Always visible */}
          <div 
            className="flex justify-between items-center p-4 cursor-pointer hover:bg-spotify-gray rounded-t-lg transition"
            onClick={() => setShowSettings(!showSettings)}
          >
            <h3 className="text-lg font-semibold">Recommendation Settings</h3>
            <span className="text-spotify-lightgray">{showSettings ? '▲ Hide' : '▼ Show'}</span>
          </div>

          {/* Collapsible Content */}
          {showSettings && (
            <div className="p-4 pt-0">
              <div className="flex justify-end gap-4 mb-4">
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    resetSettings()
                  }}
                  className="text-spotify-lightgray text-sm hover:text-white transition"
                >
                  Reset Settings
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    setShowAdvanced(!showAdvanced)
                  }}
                  className="text-spotify-lightgray text-sm hover:text-white transition"
                >
                  {showAdvanced ? 'Hide Advanced' : 'Show Advanced'}
                </button>
              </div>

              {/* Recommendation Source Toggle */}
              <div className="mb-6">
                <span className="text-spotify-lightgray text-sm block mb-2">Get recommendations based on:</span>
                <div className="flex bg-spotify-gray rounded-full p-1 w-fit">
                  <button
                    onClick={() => switchRecommendationSource('A')}
                    className={`px-4 py-2 rounded-full text-sm transition ${
                      recommendationSource === 'A'
                        ? 'bg-spotify-green text-black font-semibold' 
                        : 'text-spotify-lightgray hover:text-white'
                    }`}
                  >
                    Deck A {deckACurrent ? `(${deckACurrent.track_name.slice(0, 15)}...)` : ''}
                  </button>
                  <button
                    onClick={() => switchRecommendationSource('B')}
                    className={`px-4 py-2 rounded-full text-sm transition ${
                      recommendationSource === 'B'
                        ? 'bg-spotify-green text-black font-semibold' 
                        : 'text-spotify-lightgray hover:text-white'
                    }`}
                  >
                    Deck B {deckBCurrent ? `(${deckBCurrent.track_name.slice(0, 15)}...)` : ''}
                  </button>
                </div>
              </div>
              
              {/* Main Controls */}
              <div className="flex gap-8 items-end flex-wrap">
                <DirectionToggle 
                  label="BPM" 
                  value={bpmDirection} 
                  onChange={setBpmDirection}
                  type="bpm"
                />
                <DirectionToggle 
                  label="Energy" 
                  value={energyDirection} 
                  onChange={setEnergyDirection} 
                />
                <button
                  onClick={refreshRecommendations}
                  disabled={isRefreshing}
                  className={`bg-spotify-green text-black font-semibold px-4 py-2 rounded-full transition active:scale-95 ${
                    isRefreshing 
                      ? 'opacity-50 cursor-not-allowed' 
                      : 'hover:bg-green-400 active:bg-green-600'
                  }`}
                >
                  {isRefreshing ? '⟳ Refreshing...' : '⟳ Refresh Recommendations'}
                </button>
              </div>

              {/* Advanced Controls - Now directly below BPM/Energy */}
              {showAdvanced && (
                <div className="mt-6 pt-6 border-t border-spotify-gray">
                  <h4 className="text-sm text-spotify-lightgray mb-4">Advanced Feature Controls</h4>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <DirectionToggle 
                      label="Danceability" 
                      value={featureDirections.danceability} 
                      onChange={(v) => updateFeatureDirection('danceability', v)} 
                    />
                    <DirectionToggle 
                      label="Valence (Mood)" 
                      value={featureDirections.valence} 
                      onChange={(v) => updateFeatureDirection('valence', v)} 
                    />
                    <DirectionToggle 
                      label="Acousticness" 
                      value={featureDirections.acousticness} 
                      onChange={(v) => updateFeatureDirection('acousticness', v)} 
                    />
                    <DirectionToggle 
                      label="Instrumentalness" 
                      value={featureDirections.instrumentalness} 
                      onChange={(v) => updateFeatureDirection('instrumentalness', v)} 
                    />
                    <DirectionToggle 
                      label="Speechiness" 
                      value={featureDirections.speechiness} 
                      onChange={(v) => updateFeatureDirection('speechiness', v)} 
                    />
                    <DirectionToggle 
                      label="Liveness" 
                      value={featureDirections.liveness} 
                      onChange={(v) => updateFeatureDirection('liveness', v)} 
                    />
                    <DirectionToggle 
                      label="Loudness" 
                      value={featureDirections.loudness} 
                      onChange={(v) => updateFeatureDirection('loudness', v)} 
                    />
                  </div>
                </div>
              )}

              {/* Genre Filter - Now after Advanced */}
              <div className="mt-6 pt-6 border-t border-spotify-gray">
                <div className="flex justify-between items-center mb-3">
                  <h4 className="text-sm text-spotify-lightgray">Genre Filter</h4>
                  <button
                    onClick={suggestGenres}
                    disabled={!getSourceTrack()}
                    className={`text-sm transition ${
                      getSourceTrack() 
                        ? 'text-spotify-green hover:underline' 
                        : 'text-spotify-lightgray cursor-not-allowed'
                    }`}
                  >
                    Suggest similar genres to {getSourceTrack()?.track_genre || 'selected track'}
                  </button>
                </div>
                
                {/* Selected Genres */}
                <div className="flex flex-wrap gap-2 mb-3">
                  {selectedGenres.map((genre, i) => (
                    <span
                      key={i}
                      className="bg-spotify-green text-black px-3 py-1 rounded-full text-sm flex items-center gap-2"
                    >
                      {genre}
                      <button
                        onClick={() => setSelectedGenres(prev => prev.filter(g => g !== genre))}
                        className="hover:text-red-600"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                  {selectedGenres.length > 0 && (
                    <button
                      onClick={() => setSelectedGenres([])}
                      className="text-spotify-lightgray text-sm hover:text-white"
                    >
                      Clear all
                    </button>
                  )}
                </div>
                
                {/* Genre Dropdown */}
                <div className="relative">
                  <button
                    onClick={() => setShowGenreDropdown(!showGenreDropdown)}
                    className="bg-spotify-gray px-4 py-2 rounded-full text-sm hover:bg-spotify-lightgray hover:text-black transition"
                  >
                    + Add Genre
                  </button>
                  
                  {showGenreDropdown && (
                    <div className="absolute top-12 left-0 bg-spotify-gray rounded-lg p-2 max-h-60 overflow-y-auto z-10 w-64">
                      {allGenres
                        .filter(g => !selectedGenres.includes(g))
                        .map((genre, i) => (
                          <div
                            key={i}
                            onClick={() => {
                              setSelectedGenres(prev => [...prev, genre])
                              setShowGenreDropdown(false)
                            }}
                            className="px-3 py-2 hover:bg-spotify-darkgray rounded cursor-pointer text-sm"
                          >
                            {genre}
                          </div>
                        ))}
                    </div>
                  )}
                </div>
                
                {/* Show suggested genres info */}
                {suggestedGenres.length > 0 && (
                  <div className="mt-3 text-xs text-spotify-lightgray">
                    Similar genres based on audio features: {suggestedGenres.map(g => `${g.genre} (${g.distance.toFixed(2)})`).join(', ')}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Recommendations */}
      {recommendations.length > 0 && (
        <div className="p-6">
          <h2 className="text-xl font-bold mb-4">
            Recommendations for Deck {getTargetDeck()}
            {getSourceTrack() && (
              <span className="text-spotify-lightgray text-sm font-normal ml-2">
                (based on {getSourceTrack().track_name})
              </span>
            )}
          </h2>
          <div className="grid grid-cols-1 gap-2">
            {recommendations.map((rec, i) => {
              const playlistStatus = getTrackPlaylistStatus(rec.track)
              return (
                <div
                  key={i}
                  onClick={() => loadRecommendation(rec)}
                  className={`bg-spotify-darkgray p-4 rounded-lg hover:bg-spotify-gray active:bg-spotify-lightgray cursor-pointer transition-colors ${
                    playlistStatus ? 'border-l-4 border-spotify-green' : ''
                  }`}
                >
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <p className="font-medium">{rec.track.track_name}</p>
                        {playlistStatus && (
                          <span className="text-xs bg-spotify-green text-black px-2 py-0.5 rounded-full">
                            In Deck {playlistStatus}
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-spotify-lightgray">{rec.track.artists}</p>
                      
                      {/* Score breakdown */}
                      <div className="mt-2 flex gap-3 text-xs text-spotify-lightgray">
                        <span>BPM: {(rec.scores.bpm * 100).toFixed(0)}%</span>
                        <span>Energy: {(rec.scores.energy * 100).toFixed(0)}%</span>
                        <span>Features: {(rec.scores.features * 100).toFixed(0)}%</span>
                        <span>Harmonic: {(rec.camelot_info.camelot_score * 100).toFixed(0)}%</span>
                      </div>
                    </div>
                    
                    <div className="flex flex-col items-end gap-1 text-sm">
                      <div className="flex gap-4">
                        <span className="text-spotify-lightgray">{Math.round(rec.track.tempo)} BPM</span>
                        <span className="text-spotify-green">{rec.camelot_info.camelot_key}</span>
                      </div>
                      <span className="text-spotify-green font-bold text-lg">{(rec.total_score * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Collapsible Graph Panel */}
      {showGraphs && (
        <div className="p-6 border-t border-spotify-gray">
          <h2 className="text-xl font-bold mb-4">Setlist Flow</h2>
          {masterSetlist.length > 0 ? (
            <div className="bg-spotify-darkgray rounded-lg p-6">
              {/* Track list preview */}
              <div className="mb-6 flex flex-wrap gap-2">
                {masterSetlist.map((item, i) => (
                  <div
                    key={i}
                    className={`px-3 py-1 rounded-full text-sm ${
                      item.deck === 'A' ? 'bg-blue-600' : 'bg-purple-600'
                    }`}
                  >
                    {item.deck}{Math.ceil(item.order / 2)}: {item.track.track_name.slice(0, 15)}...
                  </div>
                ))}
              </div>

              {/* Graphs */}
              <div className="grid grid-cols-1 gap-6">
                {/* Energy Flow */}
                <div>
                  <h3 className="text-spotify-lightgray mb-2">Energy Flow</h3>
                  <ResponsiveContainer width="100%" height={150}>
                    <LineChart data={masterSetlist.map((item, i) => ({
                      name: `${item.deck}${Math.ceil(item.order / 2)}`,
                      energy: item.track.energy * 100,
                      index: i
                    }))}>
                      <XAxis dataKey="name" stroke="#B3B3B3" fontSize={12} />
                      <YAxis domain={[0, 100]} stroke="#B3B3B3" fontSize={12} />
                      <Tooltip 
                        contentStyle={{ backgroundColor: '#282828', border: 'none' }}
                        labelStyle={{ color: '#fff' }}
                      />
                      <Line 
                        type="monotone" 
                        dataKey="energy" 
                        stroke="#1DB954" 
                        strokeWidth={2}
                        dot={{ fill: '#1DB954' }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>

                {/* BPM Flow */}
                <div>
                  <h3 className="text-spotify-lightgray mb-2">BPM Flow</h3>
                  <ResponsiveContainer width="100%" height={150}>
                    <LineChart data={masterSetlist.map((item, i) => ({
                      name: `${item.deck}${Math.ceil(item.order / 2)}`,
                      bpm: Math.round(item.track.tempo),
                      index: i
                    }))}>
                      <XAxis dataKey="name" stroke="#B3B3B3" fontSize={12} />
                      <YAxis stroke="#B3B3B3" fontSize={12} />
                      <Tooltip 
                        contentStyle={{ backgroundColor: '#282828', border: 'none' }}
                        labelStyle={{ color: '#fff' }}
                      />
                      <Line 
                        type="monotone" 
                        dataKey="bpm" 
                        stroke="#1DB954" 
                        strokeWidth={2}
                        dot={{ fill: '#1DB954' }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>

                {/* Danceability Flow */}
                <div>
                  <h3 className="text-spotify-lightgray mb-2">Danceability Flow</h3>
                  <ResponsiveContainer width="100%" height={150}>
                    <LineChart data={masterSetlist.map((item, i) => ({
                      name: `${item.deck}${Math.ceil(item.order / 2)}`,
                      danceability: item.track.danceability * 100,
                      index: i
                    }))}>
                      <XAxis dataKey="name" stroke="#B3B3B3" fontSize={12} />
                      <YAxis domain={[0, 100]} stroke="#B3B3B3" fontSize={12} />
                      <Tooltip 
                        contentStyle={{ backgroundColor: '#282828', border: 'none' }}
                        labelStyle={{ color: '#fff' }}
                      />
                      <Line 
                        type="monotone" 
                        dataKey="danceability" 
                        stroke="#1DB954" 
                        strokeWidth={2}
                        dot={{ fill: '#1DB954' }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          ) : (
            <p className="text-spotify-lightgray">Add tracks to see the flow</p>
          )}
        </div>
      )}
    </div>
  )
}

export default App