import { type NextPage } from 'next'
import Head from 'next/head'
import { useRef, useState } from 'react'
import { ChatContent, type ChatItem } from '../components/ChatContent'
import { ChatInput } from '../components/ChatInput'
import { Header } from '../components/Header'
import axios from 'axios'

const Home: NextPage = () => {
    const [chatItems, setChatItems] = useState<ChatItem[]>([])
    const [waiting, setWaiting] = useState<boolean>(false)
    const scrollToRef = useRef<HTMLDivElement>(null)

    const scrollToBottom = () => {
        setTimeout(
            () => scrollToRef.current?.scrollIntoView({ behavior: 'smooth' }),
            100
        )
    }

    const handleUpdate = async (prompt: string) => {
        setWaiting(true);

        try {
            const response = await axios.post("/api/chat", {message: prompt});
            setChatItems([
                ...chatItems,
                {
                    content: prompt.replace(/\n/g, '\n\n'),
                    author: 'User',
                },
                {
                    content: response.data,
                    author: 'AI',
                },
            ]);
        } catch (error) {
            console.error(error);
        }

        setWaiting(false);
        scrollToBottom();
    }

    const handleReset = () => {
        setChatItems([])
    }

    return (
        <>
            <Head>
                <title>AI Chat Playground</title>
                <meta name="description" content="AI Chat Playground" />
                <link rel="icon" href="/favicon.ico" />
            </Head>
            <div className="flex h-screen flex-col items-center bg-gray-800">
                <section className="w-full">
                    <Header />
                </section>

                <section className="w-full flex-grow overflow-y-scroll">
                    <ChatContent chatItems={chatItems} />
                    <div ref={scrollToRef} />
                </section>

                <section className="w-full">
                    <ChatInput
                        onUpdate={handleUpdate}
                        onReset={handleReset}
                        waiting={waiting}
                    />
                </section>
            </div>
        </>
    )
}

export default Home
