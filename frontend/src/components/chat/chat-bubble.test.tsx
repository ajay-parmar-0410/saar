import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { ChatBubble } from "./chat-bubble";

describe("ChatBubble", () => {
  it("renders user message content", () => {
    render(<ChatBubble role="user" content="Hello there" />);
    expect(screen.getByText("Hello there")).toBeInTheDocument();
  });

  it("renders assistant message content", () => {
    render(<ChatBubble role="assistant" content="Hi! How can I help?" />);
    expect(screen.getByText("Hi! How can I help?")).toBeInTheDocument();
  });

  it("aligns user messages to the right", () => {
    const { container } = render(<ChatBubble role="user" content="Test" />);
    const wrapper = container.firstChild as HTMLElement;
    expect(wrapper.className).toContain("justify-end");
  });

  it("aligns assistant messages to the left", () => {
    const { container } = render(<ChatBubble role="assistant" content="Test" />);
    const wrapper = container.firstChild as HTMLElement;
    expect(wrapper.className).toContain("justify-start");
  });

  it("renders sources when provided", () => {
    const sources = [
      { title: "Article One", url: "https://a.com", source: "newsapi" },
      { title: "Article Two", url: "https://b.com", source: "hackernews" },
    ];
    render(<ChatBubble role="assistant" content="Answer" sources={sources} />);
    expect(screen.getByText("Article One")).toBeInTheDocument();
    expect(screen.getByText("Article Two")).toBeInTheDocument();
  });

  it("does not render sources section when empty", () => {
    const { container } = render(
      <ChatBubble role="assistant" content="Answer" sources={[]} />
    );
    expect(container.querySelector("a")).toBeNull();
  });

  it("source links open in new tab", () => {
    const sources = [{ title: "Link", url: "https://x.com", source: "test" }];
    render(<ChatBubble role="assistant" content="Test" sources={sources} />);
    const link = screen.getByRole("link");
    expect(link).toHaveAttribute("target", "_blank");
    expect(link).toHaveAttribute("rel", "noopener noreferrer");
  });
});
