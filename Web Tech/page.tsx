"use client"

import type React from "react"

import { useState } from "react"
import { useRouter } from "next/navigation"
import Image from "next/image"

export default function HomePage() {
  const router = useRouter()
  const [name, setName] = useState("")
  const [email, setEmail] = useState("")
  const [otp, setOtp] = useState("")
  const [showOtpInput, setShowOtpInput] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState("")
  const [generatedOtp, setGeneratedOtp] = useState("") // For demo purposes
  const [isVerified, setIsVerified] = useState(false)

  const handleSendOtp = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")

    if (!name.trim()) {
      setError("Please enter your name")
      return
    }

    if (!email.trim()) {
      setError("Please enter your email");
      return;
    }

    const emailTrimmed = email.trim().toLowerCase();
    const allowedTlds = [".com", ".net", ".org"];

    // Basic email pattern
    const basicEmailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (
      !basicEmailPattern.test(emailTrimmed) ||
      !allowedTlds.some(t => emailTrimmed.endsWith(t))
    ) {
      setError("Please enter a valid email");
      return;
    }

    setIsLoading(true)

    try {
      const response = await fetch("/api/send-otp", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || "Failed to send OTP")
      }

      setShowOtpInput(true)
      setGeneratedOtp(data.otp) // For demo - remove in production
      console.log("[v0] OTP sent to email:", email)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to send OTP")
    } finally {
      setIsLoading(false)
    }
  }

  const handleVerifyOtp = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")

    if (!otp.trim() || otp.length !== 6) {
      setError("Please enter a valid 6-digit OTP")
      return
    }

    setIsLoading(true)

    try {
      const response = await fetch("/api/send-otp", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, otp }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || "Invalid OTP")
      }

      // Store user info in localStorage
      localStorage.setItem("customerInfo", JSON.stringify({ name, email }))

      console.log("[v0] OTP verified successfully")
      setIsVerified(true)

      const saveResponse = await fetch("/api/users", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, email }),
    })

    if (!saveResponse.ok) {
      const saveError = await saveResponse.json()
      console.error("Failed to save user:", saveError.error)
    } else {
      console.log("User saved to MongoDB")
    }

    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to verify OTP")
      setIsLoading(false)
      return
    }

    setIsLoading(false)
  }

  const handleOrderTypeSelection = (type: "eat-here" | "take-home") => {
    localStorage.setItem("orderType", type)
    router.push("/menu")
  }

  return (
    <div className="min-h-screen bg-[#FFFDE3]">
      {/* Header */}
      <header className="bg-[#FFFDE3] sticky top-0 z-50 shadow-sm rounded-b-[40px]">
        <div className="max-w-[1000px] mx-auto px-8 py-4 flex items-center gap-3">
          <Image
            src="https://hebbkx1anhila5yf.public.blob.vercel-storage.com/logo-IVXQ4JWg3zR7d7S15IXHAR5pXgOXre.png"
            alt="DEVDINE Logo"
            width={80}
            height={80}
            className="object-contain"
          />
          <h1 className="text-4xl font-black text-[#353535] tracking-wide font-mono">DEVDINE</h1>
        </div>
      </header>

      {/* Banner */}
      <section className="w-full">
        <div className="relative w-full h-[300px] md:h-[400px] overflow-hidden">
          <img
            src="/delicious-asian-food-spread-on-table.jpg"
            alt="Food Banner"
            className="w-full h-full object-cover"
          />
        </div>
      </section>

      {/* Form Section */}
      <section className="max-w-md mx-auto px-4 py-12">
        {!showOtpInput ? (
          <form onSubmit={handleSendOtp} className="space-y-6">
            <div>
              <label htmlFor="name" className="block text-gray-900 font-semibold mb-2 text-lg">
                Name
              </label>
              <input
                type="text"
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Enter your name"
                className="w-full px-4 py-3 rounded-full border-2 border-gray-300 focus:border-[#c41e1e] focus:outline-none bg-white text-gray-700 placeholder-gray-400"
                required
              />
            </div>

            <div>
              <label htmlFor="email" className="block text-gray-900 font-semibold mb-2 text-lg">
                Email
              </label>
              <input
                type="email"
                id="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Enter your email"
                className="w-full px-4 py-3 rounded-full border-2 border-gray-300 focus:border-[#c41e1e] focus:outline-none bg-white text-gray-700 placeholder-gray-400"
                required
              />
            </div>

            {error && <p className="text-red-600 text-sm text-center">{error}</p>}

            <div className="flex justify-center pt-4">
              <button
                type="submit"
                disabled={isLoading}
                className="bg-[#c41e1e] hover:bg-[#a01818] text-white font-bold px-8 py-3 rounded-full transition-colors shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? "Sending..." : "Send Verification Code"}
              </button>
            </div>
          </form>
        ) : (
          <form onSubmit={handleVerifyOtp} className="space-y-6">
            <div className="text-center mb-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Verify Your Email</h2>
              <p className="text-gray-600">We sent a 6-digit code to {email}</p>
              {generatedOtp && <p className="text-sm text-green-600 mt-2">Demo OTP: {generatedOtp}</p>}
            </div>

            <div>
              <label htmlFor="otp" className="block text-gray-900 font-semibold mb-2 text-lg text-center">
                Enter Verification Code
              </label>
              <input
                type="text"
                id="otp"
                value={otp}
                onChange={(e) => setOtp(e.target.value.replace(/\D/g, "").slice(0, 6))}
                placeholder="000000"
                maxLength={6}
                className="w-full px-4 py-3 rounded-full border-2 border-gray-300 focus:border-[#c41e1e] focus:outline-none bg-white text-gray-700 placeholder-gray-400 text-center text-2xl tracking-widest"
                required
              />
            </div>

            {error && <p className="text-red-600 text-sm text-center">{error}</p>}

            {!isVerified && (
              <div className="flex justify-center pt-4">
                <button
                  type="submit"
                  disabled={isLoading || otp.length !== 6}
                  className="bg-[#c41e1e] hover:bg-[#a01818] text-white font-bold px-8 py-3 rounded-full transition-colors shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isLoading ? "Verifying..." : "Verify Code"}
                </button>
              </div>
            )}

            {!isVerified && (
              <div className="text-center">
                <button
                  type="button"
                  onClick={() => {
                    setShowOtpInput(false)
                    setOtp("")
                    setError("")
                  }}
                  className="text-[#c41e1e] hover:underline text-sm"
                >
                  Change email address
                </button>
              </div>
            )}

            {isVerified && (
              <div className="space-y-4">
                <div className="text-center">
                  <p className="text-green-600 font-semibold mb-4">✓ Email verified successfully!</p>
                  <p className="text-gray-700 font-medium mb-6">How would you like your order?</p>
                </div>
                <div className="flex items-center justify-center gap-4">
                  <button
                    type="button"
                    onClick={() => handleOrderTypeSelection("eat-here")}
                    className="bg-[#c41e1e] hover:bg-[#a01818] text-white font-bold px-8 py-3 rounded-full transition-colors shadow-lg"
                  >
                    Eat here
                  </button>
                  <span className="text-gray-600 font-semibold">or</span>
                  <button
                    type="button"
                    onClick={() => handleOrderTypeSelection("take-home")}
                    className="bg-[#c41e1e] hover:bg-[#a01818] text-white font-bold px-8 py-3 rounded-full transition-colors shadow-lg"
                  >
                    Take home
                  </button>
                </div>
              </div>
            )}
          </form>
        )}
      </section>

      {/* Footer */}
      <footer className="bg-[#c41e1e] mt-12">
        <div className="max-w-[1000px] mx-auto px-4 py-8">
          <div className="flex justify-center gap-6 mb-6">
            <a href="#" className="text-white hover:text-gray-200 transition-colors" aria-label="Facebook">
              <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" />
              </svg>
            </a>
            <a href="#" className="text-white hover:text-gray-200 transition-colors" aria-label="Instagram">
              <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z" />
              </svg>
            </a>
          </div>
          <p className="text-center text-white text-sm">DEVDINE NAJA</p>
        </div>
      </footer>

      {/* Scroll to top button */}
      <button
        onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
        className="fixed bottom-6 right-6 bg-[#c41e1e] hover:bg-[#a01818] text-white w-12 h-12 rounded-lg shadow-lg transition-colors flex items-center justify-center"
        aria-label="Scroll to top"
      >
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
        </svg>
      </button>
    </div>
  )
}
 