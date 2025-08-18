#!/bin/bash
# Spec quality validation hook
# Checks specification quality before implementation

set -e

echo "📊 Checking specification quality..."

SCORE=0
MAX_SCORE=10
WARNINGS=""

# Function to check file for criteria
check_criteria() {
    local file=$1
    local pattern=$2
    local weight=$3
    local description=$4
    
    if grep -q "$pattern" "$file" 2>/dev/null; then
        SCORE=$((SCORE + weight))
        echo "  ✅ $description (+$weight)"
        return 0
    else
        WARNINGS="$WARNINGS\n  ⚠️ Missing: $description"
        return 1
    fi
}

# Check each user story
if [ -d "user-stories" ]; then
    for story in user-stories/*.md; do
        if [ -f "$story" ]; then
            echo ""
            echo "Checking: $(basename $story)"
            echo "------------------------"
            
            STORY_SCORE=0
            
            # Check for required elements
            check_criteria "$story" "As a.*I want.*[Ss]o that" 2 "User story format"
            check_criteria "$story" "Acceptance Criteria" 2 "Acceptance criteria"
            check_criteria "$story" "Test Scenarios\|Test Cases" 1 "Test scenarios"
            check_criteria "$story" "Technical.*\|Implementation" 1 "Technical details"
            check_criteria "$story" "Priority\|Estimate" 1 "Priority/Estimation"
            check_criteria "$story" "Dependencies\|Blockers" 1 "Dependencies"
            check_criteria "$story" "Definition of Done\|DoD" 1 "Definition of Done"
            check_criteria "$story" "Edge Cases\|Error.*Handling" 1 "Edge cases"
            
            # Calculate percentage
            PERCENTAGE=$((STORY_SCORE * 100 / MAX_SCORE))
            
            echo ""
            echo "  Score: $STORY_SCORE/$MAX_SCORE ($PERCENTAGE%)"
            
            if [ $STORY_SCORE -ge 7 ]; then
                echo "  ✅ Quality gate PASSED"
            else
                echo "  ❌ Quality gate FAILED (minimum 7.0 required)"
                echo -e "$WARNINGS"
                
                echo ""
                echo "  💡 Suggestions to improve score:"
                echo "  • Add missing acceptance criteria"
                echo "  • Include test scenarios"
                echo "  • Define edge cases"
                echo "  • Specify dependencies"
                echo "  • Add technical implementation notes"
            fi
        fi
    done
else
    echo "⚠️ No user stories directory found"
    echo "Create user stories with: /user-story \"As a...\""
fi

echo ""
echo "-------------------"
echo "📈 Quality Summary:"

if [ $SCORE -ge 7 ]; then
    echo "✅ Ready for implementation"
else
    echo "❌ Needs improvement before implementation"
    echo "Run '/spec-enhance' in Claude Code to auto-improve"
fi