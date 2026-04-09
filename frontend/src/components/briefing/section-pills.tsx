interface SectionPillsProps {
  sections: string[];
  activeSection: string;
  onSelect: (section: string) => void;
}

export function SectionPills({ sections, activeSection, onSelect }: SectionPillsProps) {
  return (
    <div className="scrollbar-hide flex gap-2 overflow-x-auto pb-1">
      {sections.map((section) => {
        const isActive = section === activeSection;
        return (
          <button
            key={section}
            onClick={() => onSelect(section)}
            className={`min-h-[36px] whitespace-nowrap rounded-full px-4 py-1.5 text-sm font-semibold transition-colors ${
              isActive
                ? "bg-primary text-primary-foreground"
                : "bg-muted text-muted-foreground hover:bg-muted/80"
            }`}
          >
            {section}
          </button>
        );
      })}
    </div>
  );
}
