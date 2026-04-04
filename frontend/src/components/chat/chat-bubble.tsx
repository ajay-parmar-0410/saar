import type { ChatSource } from "@/lib/types";
import { ExternalLink } from "lucide-react";

interface ChatBubbleProps {
  role: "user" | "assistant";
  content: string;
  sources?: ChatSource[];
}

export function ChatBubble({ role, content, sources }: ChatBubbleProps) {
  const isUser = role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[85%] rounded-2xl px-4 py-2.5 ${
          isUser
            ? "rounded-br-md bg-primary text-primary-foreground"
            : "rounded-bl-md bg-muted text-foreground"
        }`}
      >
        <div className="whitespace-pre-wrap text-sm leading-relaxed">
          {content}
        </div>

        {sources && sources.length > 0 && (
          <div className="mt-3 space-y-1.5 border-t border-border/30 pt-2">
            {sources.map((src) => (
              <a
                key={src.url}
                href={src.url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 rounded-md bg-background/50 px-2.5 py-1.5 text-xs transition-colors hover:bg-background/80"
              >
                <ExternalLink className="size-3 shrink-0 text-muted-foreground" />
                <div className="min-w-0 flex-1">
                  <div className="truncate font-medium">{src.title}</div>
                  <div className="text-muted-foreground">{src.source}</div>
                </div>
              </a>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
